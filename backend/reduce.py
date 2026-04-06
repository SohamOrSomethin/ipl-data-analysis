import pandas as pd
import json
import os

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

VENUE_CITY_MAP = {
    "Sharjah Cricket Stadium": "Sharjah",
    "Dubai International Cricket Stadium": "Dubai",
    "Sheikh Zayed Stadium": "Abu Dhabi",
    "Zayed Cricket Stadium": "Abu Dhabi",

    "M Chinnaswamy Stadium": "Bangalore",
    "MA Chidambaram Stadium": "Chennai",
    "Wankhede Stadium": "Mumbai",
    "Eden Gardens": "Kolkata",
    "Arun Jaitley Stadium": "Delhi",
    "Sawai Mansingh Stadium": "Jaipur",
    "Rajiv Gandhi International Stadium": "Hyderabad",
    "Punjab Cricket Association IS Bindra Stadium": "Chandigarh",

    "SuperSport Park": "Centurion",
    "Kingsmead": "Durban",
    "Newlands": "Cape Town",
    "St George's Park": "Port Elizabeth",
    "New Wanderers Stadium": "Johannesburg",
    "Buffalo Park": "East London",
    "De Beers Diamond Oval": "Kimberley",
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

df["season"] = df["season"].astype(str).str.strip()
df["season"] = df["season"].replace(SEASON_MAP)  # fix the 2008/9 wala issue

for col in ["batting_team", "bowling_team", "match_won_by", "toss_winner"]:
    if col in df.columns:
        df[col] = df[col].apply(resolve_team)  # normalize teams in these columns

df["runs_total"] = pd.to_numeric(df["runs_total"], errors="coerce").fillna(0)
df["date"] = pd.to_datetime(df["date"], errors="coerce")


def first_non_null(series):
    # ball-by-ball dataset: take first valid value
    s = series.dropna()
    return s.iloc[0] if not s.empty else None


match_summaries = []


for match_id, g in df.groupby("match_id", sort=False):

    teams = sorted(
        set(g["batting_team"].dropna().unique()) |
        set(g["bowling_team"].dropna().unique())
    )

    # must be exactly 2 teams
    if len(teams) != 2:
        continue

    team1, team2 = teams

    # total runs per team
    team_runs = (
        g.groupby("batting_team")["runs_total"]
        .sum()
        .to_dict()
    )

    team1_runs = int(team_runs.get(team1, 0))
    team2_runs = int(team_runs.get(team2, 0))

    season = first_non_null(g["season"])
    date   = first_non_null(g["date"])

    venue = normalise_venue(first_non_null(g["venue"]))
    city  = first_non_null(g["city"])

    # fix missing city
    if not city or city == "Unknown":
        city = VENUE_CITY_MAP.get(venue, city)

    winner  = first_non_null(g["match_won_by"])
    win_out = first_non_null(g["win_outcome"])

    if (
     pd.isna(winner)
     or not str(winner).strip()
     or str(winner).strip().lower() in ["unknown", "no result", "tie", "abandoned"]
    ):
     winner = None
     result = "no_result"
    else:
     winner = resolve_team(winner)
     result = "completed"

    if result == "no_result":
     win_out = None

    pom = first_non_null(g["player_of_match"])
    if not pom or str(pom).strip().lower() == "unknown":
     pom = None

    toss_w = first_non_null(g["toss_winner"])
    if not toss_w or str(toss_w).strip().lower() == "unknown":
     toss_w = None

    toss_d = first_non_null(g["toss_decision"])
    stage  = first_non_null(g["stage"]) if "stage" in g.columns else None

    match_summaries.append({
        "match_id": int(match_id),
        "season": None if pd.isna(season) else str(season),
        "date": None if pd.isna(date) else str(pd.to_datetime(date).date()),
        "venue": venue,
        "city": city,
        "team1": team1,
        "team2": team2,
        "toss_winner": toss_w,
        "toss_decision": toss_d,
        "winner": winner,
        "result": result,
        "win_outcome": None if pd.isna(win_out) else str(win_out),
        "player_of_match": pom,
        "team1_runs": team1_runs,
        "team2_runs": team2_runs,
        "total_runs": team1_runs + team2_runs,
        "stage": None if pd.isna(stage) else (
            "group_stage" if stage == "Unknown" else stage
        )
    })

# sort chronologically
match_summaries.sort(key=lambda x: (x["date"] or "", x["match_id"]))

output_path = r"static\data\match_summary.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(match_summaries, f, indent=2, ensure_ascii=False)

print(f"Saved {len(match_summaries)} match summaries → {output_path}")