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

for col in ["batting_team", "bowling_team", "match_won_by", "toss_winner"]:
    if col in df.columns:
        df[col] = df[col].apply(resolve_team)

for col in ["runs_total"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

def first_non_null(series):
    s = series.dropna()
    return s.iloc[0] if not s.empty else None

match_rows = []

for match_id, g in df.groupby("match_id", sort=False):
    teams = sorted(
        set(g["batting_team"].dropna().unique()) |
        set(g["bowling_team"].dropna().unique())
    )

    if len(teams) != 2:
        continue

    team1, team2 = teams

    winner = first_non_null(g["match_won_by"]) if "match_won_by" in g.columns else None
    season = first_non_null(g["season"]) if "season" in g.columns else None
    venue = first_non_null(g["venue"]) if "venue" in g.columns else None
    city = first_non_null(g["city"]) if "city" in g.columns else None
    match_date = first_non_null(g["date"]) if "date" in g.columns else None
    toss_winner = first_non_null(g["toss_winner"]) if "toss_winner" in g.columns else None
    toss_decision = first_non_null(g["toss_decision"]) if "toss_decision" in g.columns else None
    player_of_match = first_non_null(g["player_of_match"]) if "player_of_match" in g.columns else None
    win_outcome = first_non_null(g["win_outcome"]) if "win_outcome" in g.columns else None

    innings_totals = (
        g.groupby(["innings", "batting_team"], as_index=False)["runs_total"]
        .sum()
        .sort_values(["innings", "batting_team"])
    )

    if innings_totals.empty:
        continue

    team_runs = (
        g.groupby("batting_team", as_index=False)["runs_total"]
        .sum()
        .set_index("batting_team")["runs_total"]
        .to_dict()
    )

    team1_runs = int(team_runs.get(team1, 0))
    team2_runs = int(team_runs.get(team2, 0))
    total_runs = team1_runs + team2_runs

    match_rows.append({
        "match_id": int(match_id),
        "team1": team1,
        "team2": team2,
        "winner": winner,
        "season": None if pd.isna(season) else str(season),
        "date": None if pd.isna(match_date) else str(pd.to_datetime(match_date).date()),
        "venue": venue,
        "city": city,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision,
        "player_of_match": player_of_match,
        "win_outcome": None if pd.isna(win_outcome) else str(win_outcome),
        "team1_runs": team1_runs,
        "team2_runs": team2_runs,
        "total_runs": total_runs
    })

matches_df = pd.DataFrame(match_rows)

if matches_df.empty:
    raise ValueError("No valid match summaries could be generated from the CSV.")

def serialize_match(row):
    return {
        "match_id": int(row["match_id"]),
        "season": row["season"],
        "date": row["date"],
        "venue": row["venue"],
        "city": row["city"],
        "winner": row["winner"],
        "win_outcome": row["win_outcome"],
        "team1_runs": int(row["team1_runs"]),
        "team2_runs": int(row["team2_runs"]),
        "total_runs": int(row["total_runs"]),
        "player_of_match": row["player_of_match"],
        "toss_winner": row["toss_winner"],
        "toss_decision": row["toss_decision"]
    }

pair_records = []

pair_keys = matches_df[["team1", "team2"]].drop_duplicates().sort_values(["team1", "team2"])

for _, pair in pair_keys.iterrows():
    team1 = pair["team1"]
    team2 = pair["team2"]

    pair_matches = matches_df[
        (matches_df["team1"] == team1) & (matches_df["team2"] == team2)
    ].copy()

    total_matches = len(pair_matches)

    team1_wins = int((pair_matches["winner"] == team1).sum())
    team2_wins = int((pair_matches["winner"] == team2).sum())

    decided_matches = team1_wins + team2_wins
    team1_win_pct = round((team1_wins / decided_matches) * 100, 2) if decided_matches else 0.0
    team2_win_pct = round((team2_wins / decided_matches) * 100, 2) if decided_matches else 0.0

    highest_match = pair_matches.loc[pair_matches["total_runs"].idxmax()]

    pair_records.append({
        "team1": team1,
        "team2": team2,
        "matches": int(total_matches),
        "team1_wins": int(team1_wins),
        "team2_wins": int(team2_wins),
        "team1_win_pct": float(team1_win_pct),
        "team2_win_pct": float(team2_win_pct),
        "highest_scoring_match": serialize_match(highest_match)
    })

pair_records = sorted(pair_records, key=lambda x: (x["team1"], x["team2"]))

output_path = "../static/data/head_to_head.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(pair_records, f, indent=2, ensure_ascii=False)

print(f"Saved {len(pair_records)} head-to-head records to {output_path}")