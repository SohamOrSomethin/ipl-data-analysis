from flask import Flask, jsonify, request,Blueprint
import pandas as pd
from flask_cors import CORS
import json
import os
from collections import defaultdict
import re
from datetime import datetime
import random




app = Flask(__name__)
CORS(app)

# ── Load & Clean ──────────────────────────────────────────
df = pd.read_parquet(r"static/data/ipl.parquet")

TEAM_ALIASES = {
    # abbreviations
    "rcb": "Royal Challengers Bangalore",
    "mi": "Mumbai Indians",
    "csk": "Chennai Super Kings",
    "kkr": "Kolkata Knight Riders",
    "rr": "Rajasthan Royals",
    "srh": "Sunrisers Hyderabad",
    "dc": "Delhi Capitals",
    "dd": "Delhi Capitals",
    "pbks": "Punjab Kings",
    "kxip": "Punjab Kings",
    "lsg": "Lucknow Super Giants",
    "gt": "Gujarat Titans",
    "gl": "Gujarat Lions",
    "rps": "Rising Pune Supergiants",
    "rpsg": "Rising Pune Supergiants",
    "pwi": "Pune Warriors India",
    "ktk": "Kochi Tuskers Kerala",
    "dcg": "Deccan Chargers",
    "pwi": "Pune Warriors",

    # canonical names
    "mumbai indians": "Mumbai Indians",
    "chennai super kings": "Chennai Super Kings",
    "kolkata knight riders": "Kolkata Knight Riders",
    "rajasthan royals": "Rajasthan Royals",
    "sunrisers hyderabad": "Sunrisers Hyderabad",
    "delhi capitals": "Delhi Capitals",
    "punjab kings": "Punjab Kings",
    "royal challengers bangalore": "Royal Challengers Bangalore",
    "lucknow super giants": "Lucknow Super Giants",
    "gujarat titans": "Gujarat Titans",
    "gujarat lions": "Gujarat Lions",
    "rising pune supergiants": "Rising Pune Supergiants",
    "pune warriors india": "Pune Warriors",
    "pune warriors": "Pune Warriors",
    "kochi tuskers kerala": "Kochi Tuskers Kerala",
    "deccan chargers": "Deccan Chargers",

    # renamed teams → canonical
    "delhi daredevils": "Delhi Capitals",
    "kings xi punjab": "Punjab Kings",
    "royal challengers bengaluru": "Royal Challengers Bangalore",
    "rising pune supergiant": "Rising Pune Supergiants",
}

TEAM_DISPLAY = {
    "Pune Warriors": "Pune Warriors India",
    "Delhi Capitals": "Delhi Capitals",
    "Punjab Kings": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bangalore",
}

HOME_CITIES = {
    "mumbai indians":              ["mumbai", "wankhede"],
    "chennai super kings":         ["chennai", "chepauk"],
    "royal challengers bangalore": ["bengaluru", "bangalore", "chinnaswamy"],
    "kolkata knight riders":       ["kolkata", "eden gardens"],
    "rajasthan royals":            ["jaipur", "sawai"],
    "delhi daredevils":            ["delhi", "feroz"],
    "delhi capitals":              ["delhi", "feroz"],
    "sunrisers hyderabad":         ["hyderabad", "rajiv gandhi"],
    "deccan chargers":             ["hyderabad", "rajiv gandhi"],
    "punjab kings":                ["mohali", "dharamsala", "mullanpur"],
    "kings xi punjab":             ["mohali", "dharamsala"],
    "lucknow super giants":        ["lucknow", "ekana"],
    "gujarat titans":              ["ahmedabad", "narendra modi"],
    "gujarat lions":               ["rajkot", "saurashtra"],
    "rising pune supergiant":      ["pune", "maharashtra"],
    "rising pune supergiants":     ["pune", "maharashtra"],
    "pune warriors india":         ["pune", "maharashtra"],
    "kochi tuskers kerala":        ["kochi", "jawaharlal"],
}

SEASON_MAP = {
    "2007/08": "2008",
    "2009/10": "2010",
    "2020/21": "2020",
}

VENUE_ALIASES = {
    "Arun Jaitley Stadium, Delhi": "Arun Jaitley Stadium",
    "Feroz Shah Kotla": "Arun Jaitley Stadium",
    "Brabourne Stadium, Mumbai": "Brabourne Stadium",
    "Dr DY Patil Sports Academy, Mumbai": "Dr DY Patil Sports Academy",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam": "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
    "Eden Gardens, Kolkata": "Eden Gardens",
    "Himachal Pradesh Cricket Association Stadium, Dharamsala": "Himachal Pradesh Cricket Association Stadium",
    "M Chinnaswamy Stadium, Bengaluru": "M Chinnaswamy Stadium",
    "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "MA Chidambaram Stadium, Chepauk": "MA Chidambaram Stadium",
    "MA Chidambaram Stadium, Chepauk, Chennai": "MA Chidambaram Stadium",
    "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur": "Maharaja Yadavindra Singh International Cricket Stadium",
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh": "Maharaja Yadavindra Singh International Cricket Stadium",
    "Maharashtra Cricket Association Stadium, Pune": "Maharashtra Cricket Association Stadium",
    "Narendra Modi Stadium, Ahmedabad": "Narendra Modi Stadium",
    "Sardar Patel Stadium, Motera": "Narendra Modi Stadium",
    "Punjab Cricket Association IS Bindra Stadium, Mohali": "Punjab Cricket Association IS Bindra Stadium",
    "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh": "Punjab Cricket Association IS Bindra Stadium",
    "Punjab Cricket Association Stadium, Mohali": "Punjab Cricket Association IS Bindra Stadium",
    "Rajiv Gandhi International Stadium, Uppal": "Rajiv Gandhi International Stadium",
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Rajiv Gandhi International Stadium",
    "Sawai Mansingh Stadium, Jaipur": "Sawai Mansingh Stadium",
    "Wankhede Stadium, Mumbai": "Wankhede Stadium",
    "Zayed Cricket Stadium, Abu Dhabi": "Zayed Cricket Stadium",
    "Sheikh Zayed Stadium": "Zayed Cricket Stadium",
    "Wankhede Stadium, Mumbai": "Wankhede Stadium",
}

def normalise_venue(name):
    if not name:
        return "Unknown"
    name = name.strip()
    return VENUE_ALIASES.get(name, name)

with open("static/data/orange_cap.json") as f:
    ORANGE_CAP = json.load(f)

with open("static/data/purple_cap.json") as f:
    PURPLE_CAP = json.load(f)

with open("static/data/teams.json") as f:
    TEAMS = json.load(f)

with open("static/data/ipl_quiz.json") as f:
    quiz = json.load(f)

with open("static/data/on_this_day.json", encoding="utf-8") as f:
    on_this_day = json.load(f)

def clean_data(df):
    # Normalize season using explicit mapping for the 3 edge cases
    df["season"] = df["season"].astype(str).str.strip()
    df["season"] = df["season"].replace(SEASON_MAP)

    # Fill NaN in numeric columns with 0
    df["runs_batter"]   = pd.to_numeric(df["runs_batter"],   errors="coerce").fillna(0)
    df["bowler_wicket"] = pd.to_numeric(df["bowler_wicket"], errors="coerce").fillna(0)
    df["runs_total"]    = pd.to_numeric(df["runs_total"],    errors="coerce").fillna(0)

    df["venue"] = df["venue"].apply(normalise_venue)

    # Strip whitespace from string columns
    for col in ["batter", "bowler", "batting_team", "bowling_team", "venue", "season"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df.dropna(subset=["batter", "bowler"])
    return df


def build_venue_stats(match_summary):
    venue_data = defaultdict(lambda: {
        "venue": "",
        "city": "",
        "total_matches": 0,
        "teams": defaultdict(lambda: {"matches": 0, "wins": 0})
    })

    for m in match_summary:
        venue = normalise_venue(m.get("venue"))
        city  = m.get("city") or "Unknown"
        team1 = m.get("team1")
        team2 = m.get("team2")
        winner = m.get("winner")

        if not team1 or not team2:
            continue

        venue_data[venue]["venue"] = venue
        venue_data[venue]["city"]  = city
        venue_data[venue]["total_matches"] += 1

        venue_data[venue]["teams"][team1]["matches"] += 1
        venue_data[venue]["teams"][team2]["matches"] += 1

        if winner == team1:
            venue_data[venue]["teams"][team1]["wins"] += 1
        elif winner == team2:
            venue_data[venue]["teams"][team2]["wins"] += 1

    # Convert to serialisable format with win % and ranking
    result = {}
    for venue, data in venue_data.items():
        teams_list = []
        for team, stats in data["teams"].items():
            win_pct = round((stats["wins"] / stats["matches"]) * 100, 2) if stats["matches"] else 0.0
            teams_list.append({
                "team": team,
                "matches": stats["matches"],
                "wins": stats["wins"],
                "losses": stats["matches"] - stats["wins"],
                "win_pct": win_pct
            })

        # Rank by win_pct desc, then wins desc as tiebreaker
        teams_list.sort(key=lambda x: (x["win_pct"], x["wins"]), reverse=True)

        result[venue] = {
            "venue": data["venue"],
            "city": data["city"],
            "total_matches": data["total_matches"],
            "teams": teams_list
        }

    return result

df = clean_data(df)
print(f" Data cleaned.")
#----------------

@app.route("/api/seasons")
def seasons():
    seasons = sorted(df["season"].dropna().astype(str).unique().tolist())
    return jsonify(seasons)

@app.route("/api/top-batters")
def top_batters():
    season = request.args.get("season", "all")
    #http://localhost:5000/api/top-batters?season=2023 will take season as 2023 toh sirf vo specific season ke milenge top batsmen

    data = df if season == "all" else df[df["season"] == season]

    result = (
        data.groupby("batter")["runs_batter"] #stack all the batters with same name into one pile
        #take that pile and look only at the runs_batter wala column
        .sum() #sum it
        .sort_values(ascending=False) #sort desc
        .head(10) #get top 10
        .reset_index() #index og table se ayega but we need 1,2,3..10 aise thats why reset 
        .rename(columns={"runs_batter": "runs"})
        #show karte waqt show as runs instead of runs batter
    )
    return jsonify(result.to_dict(orient="records"))
    # convert output to a dictionary into a format that json can understand

# ── Top 10 wicket takers ──────────────────────────────────
@app.route("/api/top-bowlers")
def top_bowlers():
    season = request.args.get("season", "all")
    data = df if season == "all" else df[df["season"] == season]

    result = (
        data.groupby("bowler")["bowler_wicket"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"bowler_wicket": "wickets"})
    )
    return jsonify(result.to_dict(orient="records"))

# ── Orange Cap (top scorer per season) ───────────────────
@app.route("/api/orange-cap")
def orange_cap():
    return jsonify(ORANGE_CAP)

# ── Purple Cap (top wicket taker per season) ──────────────
@app.route("/api/purple-cap")
def purple_cap():
    return jsonify(PURPLE_CAP)

# ── Team stats ────────────────────────────────────────────
@app.route("/api/teams")
def teams():
    unique = {
        TEAM_DISPLAY.get(resolve_team(row["team"]), resolve_team(row["team"]))
        for row in TEAMS
    }
    return jsonify(sorted(unique))

with open("static/data/players.json") as f:
    players_cache = {p["name"]: p for p in json.load(f)}
    # basically makes it faster to query players
    #toh in players.json we already have all players with runs nd wickets
    #to to optimize if seasons is "all" we can just fetch waha se stats
    #instead of querying 2 lakh entires from DB
    

@app.route("/api/players")
def players():
    name = request.args.get("name", "").strip()
    season = request.args.get("season", "all")

    if len(name) < 2:
        return jsonify([])

    if season == "all":
        matches = [
            {
                "name": p.get("full_name", p["name"]),
                "raw_name": p["name"],
                "runs": p["total_runs"],
                "balls": p["total_balls"],
                "fours": p["fours"],
                "sixes": p["sixes"],
                "wickets": p["wickets"],
            }
            for p in players_cache.values()
            if name.lower() in p["name"].lower()
             or name.lower() in p.get("full_name", "").lower()
        ]
        return jsonify(sorted(matches, key=lambda x: x["name"])[:20])

    df_filtered = df[df["season"] == season]

    matching_batters = df_filtered[
        df_filtered["batter"].str.contains(name, case=False, na=False)
    ]["batter"].unique()

    matching_bowlers = df_filtered[
        df_filtered["bowler"].str.contains(name, case=False, na=False)
    ]["bowler"].unique()

    all_names = set(matching_batters) | set(matching_bowlers)

    bat_group = df_filtered.groupby("batter")
    bowl_group = df_filtered.groupby("bowler")

    results = []
    for player_name in sorted(all_names):
        bat = bat_group.get_group(player_name) if player_name in bat_group.groups else pd.DataFrame()
        bowl = bowl_group.get_group(player_name) if player_name in bowl_group.groups else pd.DataFrame()

        results.append({
            "name": players_cache.get(player_name, {}).get("full_name", player_name),
            "raw_name": player_name,
            "runs": int(bat["runs_batter"].sum()) if not bat.empty else 0,
            "balls": int(bat["balls_faced"].sum()) if not bat.empty else 0,
            "fours": int((bat["runs_batter"] == 4).sum()) if not bat.empty else 0,
            "sixes": int((bat["runs_batter"] == 6).sum()) if not bat.empty else 0,
            "wickets": int(bowl["bowler_wicket"].sum()) if not bowl.empty else 0,
        })

    return jsonify(results[:20])

def resolve_team(name):
    key = name.strip().lower()

    # direct alias
    if key in TEAM_ALIASES:
        return TEAM_ALIASES[key]

    # reverse match (canonical already)
    for v in TEAM_ALIASES.values():
        if key == v.lower():
            return v

    return name.strip()

@app.route("/api/teams/<team>/summary")
def team_summary(team):
    season = request.args.get("season", "all") # agar season not given toh consider all

    canonical = resolve_team(team)           # "delhi daredevils" → "Delhi Daredevils"
    canonical_lower = canonical.lower() #standardize krdo in lowercase

    team_data = df[
        (df["batting_team"].str.lower() == canonical_lower) |
        (df["bowling_team"].str.lower() == canonical_lower)].copy()  #get all matches played by the team batting &bowling

    if season != "all":
        team_data = team_data[team_data["season"].astype(str) == str(season)]
        #wahi wala team data jaha pe season == given season
    
    if season == "all":
        pass
        #implement this soham bhai

    if team_data.empty:
        return jsonify({"team": canonical, "season": season, "message": "No data found"}), 404

    #wins code
    unique_matches = team_data.drop_duplicates(subset="match_id")

    history = []

    if season == "all":
     grouped = unique_matches.groupby("season")

     for s, group in grouped:
        total = len(group)
        wins = (
            group["match_won_by"].str.lower() == canonical_lower
        ).sum()

        history.append({
            "season": str(s),
            "wins": int(wins),
            "total": int(total)
        })

    history = sorted(history, key=lambda x: x["season"])

    total_matches = len(unique_matches)
    wins = (unique_matches["match_won_by"].str.lower() == canonical_lower).sum()
    #wins = count the number of matches won by jaha matches_won_by column == team name
    win_pct = round((wins / total_matches) * 100, 2) if total_matches else 0.0

    # ── Home / Away ───────────────────────────────────────────────────────────
    home_keywords = HOME_CITIES.get(canonical_lower, []) # get home cities for input team
    if home_keywords:
        pattern = "|".join(home_keywords)
        home_matches = unique_matches[
            unique_matches["venue"].str.lower().str.contains(pattern, na=False)
        ].shape[0]
        #if venue contains that pattern then home match , count waise saare home matches
    else:
        home_matches = 0
    away_matches = total_matches - home_matches

    # ── NRR ───────────────────────────────────────────────────────────────────
    batting_rows = team_data[team_data["batting_team"].str.lower() == canonical_lower]
    bowling_rows = team_data[team_data["bowling_team"].str.lower() == canonical_lower]

    runs_scored = batting_rows["runs_total"].sum()
    overs_faced = batting_rows["valid_ball"].sum() / 6.0

    runs_conceded = bowling_rows["runs_total"].sum()
    overs_bowled = bowling_rows["valid_ball"].sum() / 6.0

    nrr = round(
    (runs_scored / overs_faced) - (runs_conceded / overs_bowled),3) \
        if overs_faced > 0 and overs_bowled > 0 else 0.0
    if(season == "all"):
     nrr=0.0

    # ── Top 3 Batters ─────────────────────────────────────────────────────────
    batters = (
        batting_rows.groupby("batter")
        .agg(runs=("runs_batter", "sum"), balls=("balls_faced", "sum"))
        .reset_index()
    )
    batters["strike_rate"] = (batters["runs"] / batters["balls"] * 100).round(2)
    top_batters = (
        batters.sort_values(["runs", "strike_rate"], ascending=[False, False])
        .head(3)
        .to_dict(orient="records")
    )
    

    # ── Top 3 Bowlers ─────────────────────────────────────────────────────────
    bowlers = (
        bowling_rows.groupby("bowler")
        .agg(wickets=("bowler_wicket", "sum"), runs_conceded=("runs_total", "sum"))
        .reset_index()
    )
    top_bowlers = (
        bowlers.sort_values(["wickets", "runs_conceded"], ascending=[False, True])
        .head(3)
        .to_dict(orient="records")
    )

    return jsonify(
    {
        "team": TEAM_DISPLAY.get(canonical, canonical),
        "season":     season,
        "matches":    total_matches,
        "wins":       int(wins),
        "win_pct":    win_pct,
        "home_away":  {"home": home_matches, "away": away_matches},
        "nrr":        nrr,
        "top_batters": top_batters,
        "top_bowlers": top_bowlers,
        "history": history if season == "all" else []
    }
    )


@app.route("/api/h2h/<t1>/<t2>")
def h2h(t1, t2):
    team1 = resolve_team(t1)
    team2 = resolve_team(t2)

    with open("static/data/head_to_head.json", "r") as f:
        data = json.load(f)

    for record in data:
        if (
            (record["team1"].lower() == team1.lower() and record["team2"].lower() == team2.lower())
            or
            (record["team1"].lower() == team2.lower() and record["team2"].lower() == team1.lower())
        ):
            return jsonify(record)

    return jsonify({"error": "H2H not found"}), 404

MATCH_SUMMARY_PATH = os.path.join("static", "data", "match_summary.json")

with open(MATCH_SUMMARY_PATH, "r", encoding="utf-8") as f:
    MATCH_SUMMARY = json.load(f)

def get_pair_matches(team1, team2):
    """Return all matches between two canonical team names, order-independent."""
    t1, t2 = sorted([team1.strip(), team2.strip()])
    return [
        m for m in MATCH_SUMMARY
        if sorted([m["team1"], m["team2"]]) == [t1, t2]
    ]

# ── GET /api/h2h?team1=CSK&team2=MI&from=2018&to=2023 ──────────────────────────
@app.route("/api/h2h", methods=["GET"])
def h2h_period():
    team1_raw = request.args.get("team1", "").strip()
    team2_raw = request.args.get("team2", "").strip()
    from_season = request.args.get("from", "").strip()
    to_season   = request.args.get("to", "").strip()

    if not team1_raw or not team2_raw:
        return jsonify({"error": "team1 and team2 are required"}), 400

    team1 = resolve_team(team1_raw)
    team2 = resolve_team(team2_raw)

    matches = get_pair_matches(team1, team2)

    if not matches:
        return jsonify({"error": f"No matches found between {team1} and {team2}"}), 404

    # Filter by season range
    if from_season:
        matches = [m for m in matches if m["season"] and str(m["season"]) >= from_season]
    if to_season:
        matches = [m for m in matches if m["season"] and str(m["season"]) <= to_season]

    if not matches:
        return jsonify({"error": "No matches found in the given time period"}), 404

    # wins (ignore no result)
    team1_wins = sum(1 for m in matches if m["winner"] == team1)
    team2_wins = sum(1 for m in matches if m["winner"] == team2)
    #sum karte jao thats why 1 for m in matches

    total   = len(matches)
    decided = team1_wins + team2_wins
    no_result = total - decided

    # highest scoring (safe)
    highest = max(matches, key=lambda m: m.get("total_runs", 0)) if matches else None

    return jsonify({
        "team1": team1,
        "team2": team2,
        "from_season": from_season or None,
        "to_season":   to_season   or None,

        "matches": total,
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "no_result": no_result,

        "team1_win_pct": round((team1_wins / decided) * 100, 2) if decided else 0.0,
        "team2_win_pct": round((team2_wins / decided) * 100, 2) if decided else 0.0,

        "highest_scoring_match": highest,

        "matches_list": sorted(
            matches,
            key=lambda m: (m["date"] or "", m["match_id"])
        )
    })

# ── GET /api/h2h/venues?team1=CSK&team2=MI&from=2018&to=2023 ───────────────────
@app.route("/api/h2h/venues", methods=["GET"]) #methods GET se bascially fetch data from user
def h2h_venues():
    team1_raw = request.args.get("team1", "").strip()
    team2_raw = request.args.get("team2", "").strip()
    from_season = request.args.get("from", "").strip()
    to_season   = request.args.get("to", "").strip()
    #get allat from request agar nahi mila to blank pakdo

    if not team1_raw or not team2_raw:
        return jsonify({"error": "team1 and team2 are required"}), 400

    team1 = resolve_team(team1_raw)
    team2 = resolve_team(team2_raw)

    matches = get_pair_matches(team1, team2)
    #get all matches with team1 vs team 2 store in matches

    if not matches:
        return jsonify({"error": f"No matches found between {team1} and {team2}"}), 404

    # season filter
    if from_season:
        matches = [m for m in matches if m["season"] and str(m["season"]) >= from_season]
    if to_season:
        matches = [m for m in matches if m["season"] and str(m["season"]) <= to_season]
    
    #keep only wahi m (for m in matches) which are in range
    if not matches:
        return jsonify({"error": "No matches found in the given time period"}), 404

    # ── Aggregate per venue ─────────────────────────────────
    venue_stats = {} #dict banao

    for m in matches:
        venue = m.get("venue") or "Unknown"
        city  = m.get("city")  or None

        if venue not in venue_stats: #if doesnt exist banao ek entry
            venue_stats[venue] = {
                "venue": venue,
                "city": city,
                "matches": 0,
                "team1_wins": 0,
                "team2_wins": 0,
                "no_result": 0
            }

        venue_stats[venue]["matches"] += 1 #calc number of matches

        if m["winner"] == team1:
            venue_stats[venue]["team1_wins"] += 1
        elif m["winner"] == team2:
            venue_stats[venue]["team2_wins"] += 1
        else:
            venue_stats[venue]["no_result"] += 1

    # ── Add percentages ─────────────────────────────────────
    venues_list = []

    for v in venue_stats.values():
        decided = v["team1_wins"] + v["team2_wins"] #no ties only winners wale taken

        venues_list.append({
            **v,
            "team1_win_pct": round((v["team1_wins"] / decided) * 100, 2) if decided else 0.0,
            "team2_win_pct": round((v["team2_wins"] / decided) * 100, 2) if decided else 0.0,
        })

    # sort by matches
    venues_list.sort(key=lambda v: v["matches"], reverse=True)

    most_played = venues_list[0] if venues_list else None #1st wala will be most played 

    # min 2 matches for fortress
    qualified = [v for v in venues_list if v["matches"] >= 3] #taken to calc fortress

    team1_fortress = max(
        qualified,
        key=lambda v: v["team1_win_pct"]
    ) if qualified else None #max win pct for team1 in team 1 vs team 2

    team2_fortress = max(
        qualified,
        key=lambda v: v["team2_win_pct"]
    ) if qualified else None

    return jsonify({
        "team1": team1,
        "team2": team2,
        "from_season": from_season or None,
        "to_season":   to_season   or None,

        "most_played_venue": most_played,
        "team1_fortress": team1_fortress,
        "team2_fortress": team2_fortress,

        "venues": venues_list
    })

with open("static/data/match_summary.json", encoding="utf-8") as f:
    MATCH_SUMMARY = json.load(f)

VENUE_STATS = build_venue_stats(MATCH_SUMMARY)

@app.route("/api/venues", methods=["GET"])
def list_venues():
    venues = [
        {
            "venue": v["venue"],
            "city": v["city"],
            "total_matches": v["total_matches"]
        }
        for v in VENUE_STATS.values()
    ]
    venues.sort(key=lambda x: x["total_matches"], reverse=True)
    return jsonify(venues)

@app.route("/api/venues/search", methods=["GET"])
def search_venues():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify({"error": "q parameter is required"}), 400

    results = [
        {
            "venue": v["venue"],
            "city": v["city"],
            "total_matches": v["total_matches"]
        }
        for v in VENUE_STATS.values()
        if query in v["venue"].lower() or query in v["city"].lower()
    ]
    results.sort(key=lambda x: x["total_matches"], reverse=True)
    return jsonify(results)

@app.route("/api/venues/<path:venue_name>", methods=["GET"])
def venue_detail(venue_name):
    min_matches = int(request.args.get("min_matches", 1))

    canonical = normalise_venue(venue_name.strip())

    data = VENUE_STATS.get(canonical)
    if not data:
        for key in VENUE_STATS:
            if key.lower() == canonical.lower():
                data = VENUE_STATS[key]
                break

    if not data:
        return jsonify({"error": f"Venue '{venue_name}' not found"}), 404

    filtered_teams = [
        t for t in data["teams"]
        if t["matches"] >= min_matches
    ]

    return jsonify({
        "venue": data["venue"],
        "city": data["city"],
        "total_matches": data["total_matches"],
        "min_matches_filter": min_matches,
        "teams": filtered_teams
    })


@app.route("/on-this-day")
def get_on_this_day():
    today = datetime.now().strftime("%m-%d")

    entry = next((d for d in on_this_day if d["date"] == today), None)

    if entry:
        return jsonify(entry)

    return jsonify({
        "date": today,
        "fact": None,
        "category": "none"
    })

@app.route("/quiz")
def get_quiz():
    return jsonify(random.choice(quiz))

def get_last_over():

    last = df[
        (df["innings"] == 2) &
        (df["over"] == 19) &
        (df["ball"] == 1)
    ]

    row = last.sample(1).iloc[0]

    match = df[df["match_id"] == row.match_id]
    final = match.iloc[-1]

    batting = row.batting_team
    bowling = row.bowling_team

    target = row.runs_target
    final_score = final.team_runs

    runs_needed = target - row.team_runs

    if final.match_won_by == batting:
        wickets = 10 - final.team_wicket
        answer = f"{batting} won by {wickets} wickets"

        opt2 = f"{batting} won by {max(1, wickets-1)} wickets"
        opt3 = f"{bowling} won by {random.randint(1,8)} runs"

    else:
        margin = target - final_score
        answer = f"{bowling} won by {abs(margin)} runs"

        opt2 = f"{bowling} won by {abs(margin)+random.randint(2,6)} runs"
        opt3 = f"{batting} won by {random.randint(1,4)} wickets"

    options = [answer, opt2, opt3]
    random.shuffle(options)

    return {
        "match_id": int(row.match_id),
        "batting": batting,
        "bowling": bowling,
        "question": f"{batting} chasing vs {bowling}",
        "score": f"{row.team_runs}/{row.team_wicket}",
        "runs_needed": int(runs_needed),
        "balls_left": 6,
        "options": options,
        "answer": answer
    }

def get_collapse():

    collapse = df[
        (df["innings"] == 1) &
        (df["over"].between(9,12)) &
        (df["team_wicket"] <= 2) &
        (df["team_runs"] >= 70)
    ]

    row = collapse.sample(1).iloc[0]

    match = df[df["match_id"] == row.match_id]
    final = match[match["innings"] == 1].iloc[-1]

    batting = row.batting_team
    bowling = row.bowling_team

    actual_runs = int(final.team_runs)
    actual_wkts = int(final.team_wicket)


    overs = row.over + row.ball / 6
    rr = row.team_runs / overs
    projected = int(rr * 20)

    collapse_score = int(projected * random.uniform(0.70, 0.85))
    accelerate_score = int(projected * random.uniform(1.05, 1.20))

    collapse_wkts = min(10, actual_wkts + random.randint(1,3))
    accel_wkts = max(2, actual_wkts - random.randint(1,2))

    answer = f"{batting} finished {actual_runs}/{actual_wkts}"

    opt2 = f"{batting} finished {projected}/{max(3,actual_wkts-1)}"
    opt3 = f"{batting} finished {collapse_score}/{collapse_wkts}"
    opt4 = f"{batting} finished {accelerate_score}/{accel_wkts}"

    options = [answer, opt2, opt3, opt4]
    random.shuffle(options)

    return {
        "match_id": int(row.match_id),
        "batting": batting,
        "bowling": bowling,
        "question": f" How many runs did {batting} make against {bowling} while being {row.team_runs}/{row.team_wicket} in {row.over}.{row.ball} overs",
        "score": f"{row.team_runs}/{row.team_wicket}",
        "over": f"{row.over}.{row.ball}",
        "options": options,
        "answer": answer
    }

@app.route("/api/game/collapse")
def collapse():
    return jsonify(json.loads(json.dumps(get_collapse(), default=int)))


@app.route("/api/game/last-over")
def last_over():
    return jsonify(json.loads(json.dumps(get_last_over(), default=int)))

def get_player_moment():

    players = df[
        (df["innings"] == 1) &
        (df["over"].between(14,18)) &
        (df["batter_runs"] >= 60)
    ] #get intresting player rows

    row = players.sample(1).iloc[0] #randomly uthao and amke one row

    match = df[df["match_id"] == row.match_id] #pura match uthao
    batter = row.batter #batter ka naam

    player_df = match[match["batter"] == batter] #sirf aise balls rakho jaha apna banda battig ka raha hai
    final = player_df.iloc[-1] #player ka last ball lia 

    final_runs = int(final.batter_runs)
    out = final.wicket_kind not in [None, "", "NA"] #if last ball not none "" or NA means not out tha batsmen out = false

    batting = row.batting_team
    bowling = row.bowling_team


    if out:
        answer = f"{batter} out for {final_runs}"
    else:
        answer = f"{batter} finished {final_runs}*"


    opt2 = f"{batter} finished {final_runs + random.randint(5,20)}*"
    opt3 = f"{batter} out for {max(30, final_runs-random.randint(5,15))}"
    opt4 = f"{batter} finished {final_runs + random.randint(-10,10)}*"

    options = [answer, opt2, opt3, opt4]
    random.shuffle(options)

    return {
        "match_id": int(row.match_id),
        "batting": batting,
        "bowling": bowling,
        "player": batter,
        "score": f"{row.team_runs}/{row.team_wicket}",
        "player_score": f"{row.batter_runs} ({row.batter_balls})",
        "over": f"{row.over}.{row.ball}",
        "question": f"{batter} batting for {batting} vs {bowling}",
        "options": options,
        "answer": answer
    }

def get_chase():

    chase = df[
        (df["innings"] == 2) &
        (df["over"].between(8,15)) &
        (df["runs_target"] > 0)
    ] #matches jaha pe 2nd innings chal rahihai and over rn is between 8 and 15 and ofc runs needed hai to win

    row = chase.sample(1).iloc[0] #take random row convert to single row

    match = df[df["match_id"] == row.match_id] #pura match from that row ball by ball lia
    final = match.iloc[-1] #final = last ball of the match wala row

    batting = row.batting_team
    bowling = row.bowling_team

    target = row.runs_target
    runs = row.team_runs
    wkts = row.team_wicket

    runs_needed = target - runs
    balls_left = 120 - (row.over*6 + row.ball)

    # actual result
    if final.match_won_by == batting: #agar batting team wins while chasing theyll win by wickets na
        wickets = 10 - final.team_wicket
        answer = f"{batting} won by {wickets} wickets"

        opt2 = f"{batting} won by {max(1,wickets-1)} wickets" #take random options
        opt3 = f"{bowling} won by {random.randint(5,20)} runs"
        opt4 = f"{bowling} won by {random.randint(1,10)} runs"

    else:
        margin = target - final.team_runs
        answer = f"{bowling} won by {abs(margin)} runs"

        opt2 = f"{bowling} won by {abs(margin)+random.randint(3,12)} runs"
        opt3 = f"{batting} won by {random.randint(1,5)} wickets"
        opt4 = f"{batting} won by {random.randint(1,3)} wickets"

    options = [answer, opt2, opt3, opt4]
    random.shuffle(options)

    return {
        "match_id": int(row.match_id),
        "batting": batting,
        "bowling": bowling,
        "target": int(target),
        "score": f"{runs}/{wkts}",
        "runs_needed": int(runs_needed),
        "balls_left": int(balls_left),
        "question": f"{batting} need {int(runs_needed)} runs in {int(balls_left)} balls against {bowling}",
        "options": options,
        "answer": answer
    }

@app.route("/api/game/player")
def player():
    return jsonify(json.loads(json.dumps(get_player_moment(), default=int)))

@app.route("/api/game/chase")
def chase():
   return jsonify(json.loads(json.dumps(get_chase(), default=int)))

MIN_MATCHES       = 20
BOWLER_MIN_MATCHES = 20
BOWLER_MIN_WICKETS = 15

@app.route('/api/goat')
def goat():
    with open("static/data/players.json") as f:
     players = json.load(f)

    role  = request.args.get('role', 'batter')   # ?role=batter or ?role=bowler
    limit = min(int(request.args.get('limit', 10)), 25)  # ?limit=10, max 25

    if role == 'bowler':
        qualified = [
            p for p in players
            if p.get('bowler_goat_score', 0) > 0
            and p.get('matches', 0) >= BOWLER_MIN_MATCHES
            and p.get('wickets', 0) >= BOWLER_MIN_WICKETS
        ]
        sort_key = 'bowler_goat_score'
    else:
        qualified = [
            p for p in players
            if p.get('batter_goat_score', 0) > 0
            and p.get('matches', 0) >= MIN_MATCHES
        ]
        sort_key = 'batter_goat_score'

    top = sorted(qualified, key=lambda x: x[sort_key], reverse=True)[:limit]

    # Add rank + pluck only what the frontend needs
    result = []
    for i, p in enumerate(top, 1):
        result.append({
            "rank":     i,
            "name": p.get("full_name", p["name"]),
            "goat_score": p[sort_key],
            "breakdown":  p.get(
                "batter_goat_breakdown" if role == "batter" else "bowler_goat_breakdown",
                {}
            ),
            # core stats for display
            "stats": _goat_stats(p, role)
        })

    return jsonify({
        "role":    role,
        "count":   len(result),
        "players": result
    })


def _goat_stats(p, role):
    """Pluck display stats depending on role."""
    if role == "batter":
        return {
            "matches":             p.get("matches", 0),
            "runs":                p.get("total_runs", 0),
            "batting_avg":         p.get("batting_avg", 0),
            "strike_rate":         p.get("strike_rate", 0),
            "seasons":             p.get("seasons_count", 0),
            "fours":               p.get("fours", 0),
            "sixes":               p.get("sixes", 0),
            "boundary_pct":        p.get("boundary_pct", 0),
            "knockout_runs":       p.get("knockout_runs", 0),
            "knockout_avg":        p.get("knockout_avg", 0),
            "runs_contribution_pct": p.get("runs_contribution_pct", 0),
        }
    else:
        return {
            "matches":                    p.get("matches", 0),
            "wickets":                    p.get("wickets", 0),
            "economy":                    p.get("economy", 0),
            "bowling_avg":                p.get("bowling_avg", 0),
            "bowling_sr":                 p.get("bowling_sr", 0),
            "seasons":                    p.get("seasons_count", 0),
            "bowling_role":               p.get("bowling_role", "N/A"),
            "knockout_wickets":           p.get("knockout_wickets", 0),
            "knockout_economy":           p.get("knockout_economy", 0),
            "wickets_per_match":          p.get("wickets_per_match", 0),
        }
    
def get_recent_form(team_canonical, last_n=5, before_date=None):
    team_matches = [
        m for m in MATCH_SUMMARY
        if m.get("team1") == team_canonical or m.get("team2") == team_canonical
        and (before_date is None or m.get("date", "") < before_date)]
    # desc sort by dates
    team_matches.sort(key=lambda m: m.get("date", ""), reverse=True)
    recent = team_matches[:last_n] #last n tak hi rakho
    if not recent:
        return 50.0  #agar recent nahi hai toh take as 50
    wins = sum(1 for m in recent if m.get("winner") == team_canonical)
    return round(wins / len(recent) * 100, 2) #nahi to return win pct

def get_current_season_form(team_canonical, current_season, before_date=None):
    """Win % in current season only — much more relevant than all-time last 5"""
    season_matches = [
        m for m in MATCH_SUMMARY
        if (m.get("team1") == team_canonical or m.get("team2") == team_canonical)
        and str(m.get("season")) == str(current_season)
        and (before_date is None or m.get("date", "") < before_date)
    ]
    if not season_matches:
        return 50.0
    wins = sum(1 for m in season_matches if m.get("winner") == team_canonical)
    return round(wins / len(season_matches) * 100, 2)

def get_venue_winpct(team_canonical, venue_name, before_date=None):
    canonical_venue = normalise_venue(venue_name)
    venue_data = VENUE_STATS.get(canonical_venue)
    print([t["team"] for t in venue_data["teams"]])

    if not venue_data:
        return 50.0  # nahi mila venue to 50 rakho (neutral)
    for t in venue_data["teams"]:
        if t["team"].lower() == team_canonical.lower():
            return t["win_pct"] if t["matches"] >= 3 else 50.0 #agar matches at that venue > 3 return vo venue ka winpct
    return 50.0

def get_venue_winpct(team_canonical, venue_name, before_date=None):
    canonical_venue = normalise_venue(venue_name)

    if before_date is None:
        # Live mode — use precomputed VENUE_STATS (fast)
        venue_data = VENUE_STATS.get(canonical_venue)
        if not venue_data:
            return 50.0
        for t in venue_data["teams"]:
            if t["team"].lower() == team_canonical.lower():
                return t["win_pct"] if t["matches"] >= 3 else 50.0
        return 50.0

    else:
        # Backtest mode — filter MATCH_SUMMARY by date (accurate)
        venue_matches = [
            m for m in MATCH_SUMMARY
            if normalise_venue(m.get("venue", "")) == canonical_venue
            and m.get("date", "") < before_date
            and m.get("result") == "completed"
            and m.get("winner")
        ]

        if len(venue_matches) < 3:
            return 50.0

        team_matches = [
            m for m in venue_matches
            if m.get("team1") == team_canonical or m.get("team2") == team_canonical
        ]

        if len(team_matches) < 3:
            return 50.0

        wins = sum(1 for m in team_matches if m.get("winner") == team_canonical)
        return round(wins / len(team_matches) * 100, 2)
    
def get_home_boost(team_canonical, venue_name):
    keywords = HOME_CITIES.get(team_canonical.lower(), [])
    venue_lower = venue_name.lower()
    if any(kw in venue_lower for kw in keywords): #agar homegroun advantage rahega toh 60 else 40
        return 60.0
    return 40.0

def get_toss_score(toss_winner, team_canonical, toss_decision, venue_name):
    if not toss_winner:
        return 50.0  # no toss info neutral

    won_toss = toss_winner.lower() == team_canonical.lower()
    if not won_toss:
        return 40.0  # lost toss → slight disadvantage

    # Not enough info to judge venue preference
    if not venue_name or venue_name == "Unknown":
        return 60.0  # won toss, but no venue data  small boost only

    canonical_venue = normalise_venue(venue_name)

    # All decided matches at this venue
    venue_matches = [
        m for m in MATCH_SUMMARY
        if normalise_venue(m.get("venue", "")) == canonical_venue
        and m.get("result") == "completed"
        and m.get("winner")
    ]

    if len(venue_matches) < 5:
        return 60.0  # too few matches means small boost

    # Matches where team batted first (won toss + chose bat)
    bat_first_matches = [
        m for m in venue_matches
        if m.get("toss_decision") == "bat"
    ]

    # Matches where team fielded first (won toss + chose field)
    field_first_matches = [
        m for m in venue_matches
        if m.get("toss_decision") == "field"
    ]

    # Win % for bat-first team at this venue
    bat_first_wins = sum(
        1 for m in bat_first_matches
        if m.get("toss_winner") == m.get("winner")  # toss winner batted and won
    )
    bat_first_win_pct = (
        bat_first_wins / len(bat_first_matches)
        if bat_first_matches else 0.5
    )

    # Win % for field-first team at this venue
    field_first_wins = sum(
        1 for m in field_first_matches
        if m.get("toss_winner") == m.get("winner")  # toss winner fielded and won
    )
    field_first_win_pct = (
        field_first_wins / len(field_first_matches)
        if field_first_matches else 0.5
    )

    # Now score based on whether the decision aligns with venue tendency
    if toss_decision == "bat":
        if bat_first_win_pct > 0.52:
            return 68.0   # good call  venue favours batting first
        elif bat_first_win_pct < 0.48:
            return 52.0   # poor call venue actually favours chasing
        else:
            return 60.0   # neutral venue, won toss

    elif toss_decision == "field":
        if field_first_win_pct > 0.52:
            return 68.0   # good call  venue favours chasing
        elif field_first_win_pct < 0.48:
            return 52.0   # poor call  venue favours batting first
        else:
            return 60.0   # neutral venue, won toss

    return 60.0  # toss_decision unknown but won toss

def get_pair_matches_before(team1, team2, before_date=None):
    return [
        m for m in MATCH_SUMMARY
        if sorted([m.get("team1"), m.get("team2")]) == sorted([team1, team2])
        and (before_date is None or m.get("date", "") < before_date)  # ← only past matches
    ]

@app.route('/api/predict/winner', methods=['GET'])
def predict_winner():
    team1_raw = request.args.get('team1', '').strip()
    team2_raw = request.args.get('team2', '').strip()
    venue_raw = request.args.get('venue', '').strip()
    toss_winner_raw = request.args.get('toss_winner', '').strip()
    toss_decision = request.args.get('toss_decision', '').strip().lower() 

    if not team1_raw or not team2_raw:
        return jsonify({"error": "team1 and team2 are required"}), 400

    team1 = resolve_team(team1_raw)
    team2 = resolve_team(team2_raw)
    toss_winner = resolve_team(toss_winner_raw) if toss_winner_raw else None
    venue = normalise_venue(venue_raw) if venue_raw else "Unknown"

    team_matches = [m for m in MATCH_SUMMARY if m.get("team1") == team1 or m.get("team2") == team1]
    team_matches.sort(key=lambda m: m.get("date", ""), reverse=True)
    print(team_matches[:5])

    # ── Pull features ────────────────────────────────────────────────────────
    # H2H win %
    pair_matches = get_pair_matches(team1, team2)
    decided = [m for m in pair_matches if m.get("winner") in [team1, team2]]
    h2h_t1 = round(sum(1 for m in decided if m["winner"] == team1) / len(decided) * 100, 2) if decided else 50.0 
    #bascially count the number of wins of team1 from decided matches between team 1 and team 2 (ye pair matches se aya)
    h2h_t2 = round(100 - h2h_t1, 2)

    # Recent form (last 5 matches)
    form_t1 = get_recent_form(team1, last_n=5)
    form_t2 = get_recent_form(team2, last_n=5)

    # Venue win %
    venue_t1 = get_venue_winpct(team1, venue)
    venue_t2 = get_venue_winpct(team2, venue)

    # Home/away boost
    home_t1 = get_home_boost(team1, venue)
    home_t2 = get_home_boost(team2, venue)

    # Toss
    toss_t1 = get_toss_score(toss_winner, team1, toss_decision, venue)
    toss_t2 = get_toss_score(toss_winner, team2, toss_decision, venue)

    # ── Weighted score ───────────────────────────────────────────────────────
    WEIGHTS = {
        "h2h":    0.30,
        "form":   0.25,
        "venue":  0.20,
        "home":   0.15,
        "toss":   0.10,
    }

    raw_t1 = (
        WEIGHTS["h2h"]   * h2h_t1   +
        WEIGHTS["form"]  * form_t1  +
        WEIGHTS["venue"] * venue_t1 +
        WEIGHTS["home"]  * home_t1  +
        WEIGHTS["toss"]  * toss_t1
    )
    raw_t2 = (
        WEIGHTS["h2h"]   * h2h_t2   +
        WEIGHTS["form"]  * form_t2  +
        WEIGHTS["venue"] * venue_t2 +
        WEIGHTS["home"]  * home_t2  +
        WEIGHTS["toss"]  * toss_t2
    )

    # Normalise so both sum to 100
    total = raw_t1 + raw_t2
    win_pct_t1 = round(raw_t1 / total * 100, 1) if total > 0 else 50.0
    win_pct_t2 = round(100 - win_pct_t1, 1)

    predicted_winner = team1 if win_pct_t1 >= win_pct_t2 else team2
    confidence = "high" if abs(win_pct_t1 - win_pct_t2) > 15 else "medium" if abs(win_pct_t1 - win_pct_t2) > 7 else "low"

    return jsonify({
        "team1": team1,
        "team2": team2,
        "venue": venue,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision or None,
        "predicted_winner": predicted_winner,
        "confidence": confidence,
        "win_probability": {
            team1: win_pct_t1,
            team2: win_pct_t2,
        },
        "factors": {
            "h2h_winpct":      {"team1": h2h_t1,   "team2": h2h_t2},
            "recent_form":     {"team1": form_t1,   "team2": form_t2},
            "venue_winpct":    {"team1": venue_t1,  "team2": venue_t2},
            "home_advantage":  {"team1": home_t1,   "team2": home_t2},
            "toss_score":      {"team1": toss_t1,   "team2": toss_t2},
        }
    })




if __name__ == "__main__":
    app.run(debug=True, port=5000)