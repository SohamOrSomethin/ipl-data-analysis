from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS
import json
import os


app = Flask(__name__)
CORS(app)

# ── Load & Clean ──────────────────────────────────────────
df = pd.read_csv("../data/IPL.csv", low_memory=False)

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
    #take ip as namea nd season konsa tha
    #if no name null, if no season consider all seasns

    if len(name) < 2:
        return jsonify([])
    #if name is less than 2 characters return null list seedha ex: k, l, " "

    if season != "all":
        df_filtered = df[df["season"] == season]
    else:
        df_filtered = df

        #agar all nahi hai toh df take by season


    matching_batters = df_filtered[df_filtered["batter"].str.contains(name, case=False, na=False)]["batter"].unique()
    #find saare batsmen with that name
    matching_bowlers = df_filtered[df_filtered["bowler"].str.contains(name, case=False, na=False)]["bowler"].unique()
    #find saare bowler with that name
    all_names = set(matching_batters) | set(matching_bowlers)
    #make it into a set

    if season == "all":
        matches = [p for p in players_cache.values() 
                   if name.lower() in p["name"].lower()]
        return jsonify(sorted(matches, key=lambda x: x["name"]))
    
    #agar all hai toh cache mai jo players load kiye the waha se lelo seedha stats
            

    results = []
    for player_name in sorted(all_names):
        bat = df_filtered[df_filtered["batter"] == player_name]
        #wo wala bat jaha batter name == player name
        bowl = df_filtered[df_filtered["bowler"] == player_name]
        #vo wala bowl jaha bowler name == player name

        results.append({
            "name": player_name,
            "runs": int(bat["runs_batter"].sum()),
            "balls": int(bat["balls_faced"].sum()),
            "fours": int((bat["runs_batter"] == 4).sum()),
            "sixes": int((bat["runs_batter"] == 6).sum()),
            "wickets": int(bowl["bowler_wicket"].sum()),
        })
        #get stats and jsonify

    return jsonify(results)

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)