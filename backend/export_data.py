import pandas as pd
import json
import os

SEASON_MAP = {
    "2007/08": "2008",
    "2009/10": "2010",
    "2020/21": "2020",
}

df = pd.read_csv(r"../data/IPL.csv", low_memory=False)

df["season"] = df["season"].astype(str).str.strip().replace(SEASON_MAP)
df["runs_batter"]   = pd.to_numeric(df["runs_batter"],   errors="coerce").fillna(0)
df["bowler_wicket"] = pd.to_numeric(df["bowler_wicket"], errors="coerce").fillna(0)
df["runs_total"]    = pd.to_numeric(df["runs_total"],    errors="coerce").fillna(0)
for col in ["batter", "bowler", "batting_team", "bowling_team", "venue", "season"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
df = df.dropna(subset=["batter", "bowler"])

os.makedirs("static/data", exist_ok=True)

# ── 1. players.json ───────────────────────────────────────
batting = (
    df.groupby("batter") #group by batter name 
    .agg(
        runs=("runs_batter", "sum"), #total runs
        balls=("balls_faced", "sum"), #total balls faced
        fours=("runs_batter", lambda x: (x == 4).sum()), #total 4s
        sixes=("runs_batter", lambda x: (x == 6).sum()), #total 6s
    )
    .reset_index() #reset indexing 
    .rename(columns={"batter": "name"}) 
)
bowling = (
    df.groupby("bowler")
    .agg(wickets=("bowler_wicket", "sum"))
    .reset_index()
    .rename(columns={"bowler": "name"})
)
players = batting.merge(bowling, on="name", how="outer").fillna(0)
#saare players nikale bowlers + batsmen also and took OUTER merge 
#outer is basiaclly union dono ka sab ayega
players["strike_rate"] = ((players["runs"] / players["balls"]) * 100).round(2)
players["strike_rate"] = players["strike_rate"].fillna(0)
 #strike rate nikala and added to new column called strike rate and NaN (0 balls faced) raha to make strike rate 0, nahi to divided by 0 hoga

for col in ["runs", "balls", "fours", "sixes", "wickets"]:
    players[col] = players[col].astype(int)

players = players.to_dict(orient="records") #converted to dictionary and then to json

with open("static/data/players.json", "w") as f:
    json.dump(players, f)
print(f" players.json — {len(players)} players")

# ── 2. teams.json ─────────────────────────────────────────
# wins per team per season
teams = (
    df.groupby(["season", "batting_team"])["runs_total"] #group by season AND team waha se total runs pe focus karo 
    #(For each match hoga ye toh sum karo)
    .sum()
    .reset_index()
    .rename(columns={"batting_team": "team", "runs_total": "total_runs"})
    .to_dict(orient="records")
)
with open("static/data/teams.json", "w") as f:
    json.dump(teams, f)
print(f" teams.json — {len(teams)} entries")

# ── 3. records.json ───────────────────────────────────────
records = {
    "most_runs": df.groupby("batter")["runs_batter"].sum().idxmax(),
    "most_wickets": df.groupby("bowler")["bowler_wicket"].sum().idxmax(),
    "total_runs": int(df["runs_total"].sum()),
    "total_wickets": int(df["bowler_wicket"].sum()),
    "highest_score": int(df.groupby(["match_id", "batter"])["runs_batter"].sum().max()),
}
# Calculate Best Bowling (Wickets/Runs)
best_b = df.groupby(["match_id", "bowler"]).agg(wickets=("bowler_wicket", "sum"), runs=("runs_bowler", "sum")).sort_values(["wickets", "runs"], ascending=[False, True]).iloc[0]
records["best_bowling"] = f"{int(best_b['wickets'])}/{int(best_b['runs'])}"

with open("static/data/records.json", "w") as f:
    json.dump(records, f)
print(f" records.json")

seasons = sorted(df["season"].unique().tolist())
with open("static/data/seasons.json", "w") as f:
    json.dump(seasons, f)
print(" seasons.json")

# 5. orange_cap.json
orange_cap = (
    df.groupby(["season", "batter"])["runs_batter"]
    .sum().reset_index()
    .sort_values(["season", "runs_batter"], ascending=[True, False])
    .groupby("season").first().reset_index()
    .rename(columns={"runs_batter": "runs"})
    .to_dict(orient="records")
)
with open("static/data/orange_cap.json", "w") as f:
    json.dump(orange_cap, f)
print(" orange_cap.json")

# 6. purple_cap.json
purple_cap = (
    df.groupby(["season", "bowler"])["bowler_wicket"]
    .sum().reset_index()
    .sort_values(["season", "bowler_wicket"], ascending=[True, False])
    .groupby("season").first().reset_index()
    .rename(columns={"bowler_wicket": "wickets"})
    .to_dict(orient="records")
)
with open("static/data/purple_cap.json", "w") as f:
    json.dump(purple_cap, f)
print(" purple_cap.json")

print("\nAll files exported to static/data/")