from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app)

# ── Load & Clean ──────────────────────────────────────────
df = pd.read_csv("../data/IPL.csv")

SEASON_MAP = {
    "2007/08": "2008",
    "2009/10": "2010",
    "2020/21": "2020",
}

def clean_data(df):
    # Normalize season using explicit mapping for the 3 edge cases
    df["season"] = df["season"].astype(str).str.strip()
    df["season"] = df["season"].replace(SEASON_MAP)

    # Fill NaN in numeric columns with 0
    df["runs_batter"]   = pd.to_numeric(df["runs_batter"],   errors="coerce").fillna(0)
    df["bowler_wicket"] = pd.to_numeric(df["bowler_wicket"], errors="coerce").fillna(0)
    df["runs_total"]    = pd.to_numeric(df["runs_total"],    errors="coerce").fillna(0)

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
    return jsonify(sorted(df["season"].unique().tolist()))

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
    result = (
        df.groupby(["season", "batter"])["runs_batter"]
        .sum()
        .reset_index()
        .sort_values(["season", "runs_batter"], ascending=[True, False])
        .groupby("season")
        .first()
        .reset_index()
        .rename(columns={"runs_batter": "runs"})
    )
    return jsonify(result.to_dict(orient="records"))

# ── Purple Cap (top wicket taker per season) ──────────────
@app.route("/api/purple-cap")
def purple_cap():
    result = (
        df.groupby(["season", "bowler"])["bowler_wicket"]
        #basically , aise group karo ki bowlers with same name and sum are clubbed into a stack, then look at bowler wicket from that stack and sum it
        .sum()
        .reset_index()
        .sort_values(["season", "bowler_wicket"], ascending=[True, False])
        #sort seasons asc and wicekts desc
        .groupby("season")
        .first()
        #abhi this is tricky toh hua aisa we have all the bowlers in every season with their sum of wickets sorted in desc, toh PEHELA row will always be the purple cap when you sort by season bcuz desc mai FIRST wala will always be leading wicket taker
        .reset_index()
        .rename(columns={"bowler_wicket": "wickets"})
    )
    return jsonify(result.to_dict(orient="records"))

# ── Team stats ────────────────────────────────────────────
@app.route("/api/teams")
def teams():
    return jsonify(sorted(df["batting_team"].dropna().unique().tolist()))
#saare batting teams lo, NA udao, unqiue wala rakho and list mai return karo

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
            "balls_faced": int(bat["balls_faced"].sum()),
            "fours": int((bat["runs_batter"] == 4).sum()),
            "sixes": int((bat["runs_batter"] == 6).sum()),
            "wickets": int(bowl["bowler_wicket"].sum()),
        })
        #get stats and jsonify

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=5000)