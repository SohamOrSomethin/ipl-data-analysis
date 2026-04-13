"""
preprocess.py — IPL Stats Dashboard
Run once at startup (or manually) to generate all static JSON files.

Outputs → static/data/
  players.json      enriched career stats + batter GOAT scores
"""

import os
import json
import math
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# go one level up → project root
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "IPL.csv")
OUT_DIR = os.path.join(BASE_DIR, "static", "data")

os.makedirs(OUT_DIR, exist_ok=True)
# ── Constants ─────────────────────────────────────────────────────────────────
MIN_MATCHES       = 20          # minimum matches to qualify for GOAT ranking
POWERPLAY_OVERS   = 6           # overs 1–6
DEATH_OVERS_START = 16          # overs 16–20

OPENER_POSITIONS  = {1, 2}
TOP_ORDER         = {1, 2, 3, 4}
FINISHER_POS      = {5, 6, 7, 8}

KNOCKOUT_STAGES   = {"final", "qualifier 1", "qualifier 2", "eliminator",
                     "qualifier", "semi final", "semifinal"}

# GOAT component weights (batter)
GOAT_WEIGHTS = {
    "volume_dominance":    0.25,
    "consistency":         0.20,
    "impact_moments":      0.25,
    "boundary_aggression": 0.10,   # ← down from 0.15
    "longevity":           0.20,   # ← up from 0.15
}

BOWLER_MIN_MATCHES = 20
BOWLER_MIN_WICKETS = 15

GOAT_WEIGHTS_BOWLER = {
    "wicket_taking":   0.30,
    "economy":         0.20,
    "impact_moments":  0.25,
    "phase_bowling":   0.15,
    "longevity":       0.10,
}

SEASON_MAP = {
    "2007/08": "2008",
    "2009/10": "2010",
    "2020/21": "2020",
}
# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD & CLEAN
# ─────────────────────────────────────────────────────────────────────────────
def npwhere(condition, x, y):
    import numpy as _np  # use alias so the find-replace didn't touch this
    result = _np.where(condition, x, y)
    if hasattr(condition, 'index'):
        return pd.Series(result, index=condition.index)
    return pd.Series(result)

def load_data() -> pd.DataFrame:
    print("📂  Loading CSV …")
    df = pd.read_csv(DATA_PATH, low_memory=False)

    # Normalise column names (strip whitespace just in case)
    df.columns = df.columns.str.strip()

    # Coerce numeric columns we rely on
    numeric_cols = [
        "runs_batter", "runs_total", "balls_faced", "valid_ball",
        "batter_runs", "batter_balls", "bowler_wicket",
        "team_runs", "over", "bat_pos", "innings",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Normalise stage to lowercase for set lookups
    if "stage" in df.columns:
        df["stage"] = df["stage"].astype(str).str.strip().str.lower()

    # season as string
    df["season"] = df["season"].astype(str).str.strip()
    df["season"] = df["season"].replace(SEASON_MAP)

    print(f"   ✓  {len(df):,} rows | {df['match_id'].nunique():,} matches "
          f"| {df['season'].nunique()} seasons")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. HELPER — min-max normalise a Series to 0–100
# ─────────────────────────────────────────────────────────────────────────────

def minmax(series: pd.Series, cap: float = None) -> pd.Series:
    """Normalise Series to [0, 100].  Optionally cap raw values first."""
    s = series.copy().astype(float)
    if cap is not None:
        s = s.clip(upper=cap)
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(50.0, index=s.index)          # all same → mid-point
    return (s - lo) / (hi - lo) * 100


# ─────────────────────────────────────────────────────────────────────────────
# 3. BUILD BATTER STATS
# ─────────────────────────────────────────────────────────────────────────────

def build_batter_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per batter with ALL fields needed for GOAT scoring.
    Works from ball-by-ball data; final ball of each innings gives
    the per-innings cumulative batter_runs / batter_balls via last-row trick.
    """
    print("🏏  Building batter stats …")

    # ── 3a. Per-innings final state ──────────────────────────────────────────
    # Last delivery of each (match_id, innings, batter) gives cumulative totals
    bat_df = df[df["batter"].notna() & (df["batter"] != "")].copy()

    last_ball = (
        bat_df
        .sort_values(["match_id", "innings", "over", "ball"])
        .groupby(["match_id", "innings", "batter"], as_index=False)
        .last()
        [["match_id", "innings", "batter", "batter_runs", "batter_balls",
          "bat_pos", "player_out", "season", "stage",
          "team_runs",        # cumulative team score at end of innings (proxy)
          "over"]]
    )

    # was this batter dismissed this innings?
    last_ball["dismissed"] = (
        last_ball["player_out"].notna() &
        (last_ball["player_out"].astype(str).str.strip() != "") &
        (last_ball["player_out"].astype(str).str.lower() != "nan") &
        (last_ball["player_out"] == last_ball["batter"])
    ).astype(int)

    # ── 3b. Career-level aggregates ─────────────────────────────────────────
    career = last_ball.groupby("batter", as_index=False).agg(
        innings       = ("match_id",    "count"),
        matches       = ("match_id",    "nunique"),
        total_runs    = ("batter_runs", "sum"),
        total_balls   = ("batter_balls","sum"),
        dismissals    = ("dismissed",   "sum"),
        seasons_count = ("season",      "nunique"),
        not_outs      = ("dismissed",   lambda x: (x == 0).sum()),
        bat_pos_mode  = ("bat_pos",     lambda x: int(x.mode().iloc[0])
                                                   if len(x) > 0 else 9),
    )
    career["batting_avg"] = np.clip(
    npwhere(
        career["dismissals"] > 0,
        career["total_runs"] / career["dismissals"],
        career["total_runs"] / career["innings"].clip(lower=1)
    ),a_min=None, a_max=120).round(2)

    # ── 3c. Boundary counts (ball-level) ────────────────────────────────────
    four_df  = bat_df[bat_df["runs_batter"] == 4].groupby("batter").size().rename("fours")
    six_df   = bat_df[bat_df["runs_batter"] == 6].groupby("batter").size().rename("sixes")
    career   = career.merge(four_df, on="batter", how="left")
    career   = career.merge(six_df,  on="batter", how="left")
    career[["fours","sixes"]] = career[["fours","sixes"]].fillna(0).astype(int)

    career["boundary_runs"] = career["fours"] * 4 + career["sixes"] * 6
    career["boundary_pct"]  = npwhere(
        career["total_runs"] > 0,
        career["boundary_runs"] / career["total_runs"] * 100, 0
    ).round(2)
    career["six_rate"] = npwhere(
        career["total_balls"] > 0,
        career["sixes"] / career["total_balls"] * 100, 0
    ).round(2)

    # ── 3d. Strike rate ──────────────────────────────────────────────────────
    career["strike_rate"] = npwhere(
        career["total_balls"] > 0,
        career["total_runs"] / career["total_balls"] * 100, 0
    ).round(2)

    
    # ── 3e. Team runs contribution (FIXED) ──────────────────────────────────────
    # Step 1: total runs scored by team in each innings
    innings_team_total = (
    df.groupby(["match_id", "innings"])["runs_total"]
      .sum()
      .reset_index()
      .rename(columns={"runs_total": "innings_team_runs"})
    )

   # Step 2: which innings did each batter appear in?
    batter_innings = (
    bat_df.groupby(["batter", "match_id", "innings"])
          .size()
          .reset_index()[["batter", "match_id", "innings"]]
    )

  # Step 3: merge to get team total for each innings the batter played
    batter_innings = batter_innings.merge(innings_team_total, on=["match_id","innings"], how="left")

   # Step 4: sum team runs across all innings this batter appeared in
    team_total_in_batter_innings = (
    batter_innings.groupby("batter")["innings_team_runs"]
                  .sum()
                  .rename("team_runs_in_innings_played")
    )

    career = career.merge(team_total_in_batter_innings, on="batter", how="left")  # still named "batter" at this point
    career["team_runs_in_innings_played"] = career["team_runs_in_innings_played"].fillna(0)
    career["runs_contribution_pct"] = np.round(npwhere(
    career["team_runs_in_innings_played"] > 0,
    career["total_runs"] / career["team_runs_in_innings_played"] * 100,
    0
    ), 2)

    # ── 3f. Seasonal batting averages ────────────────────────────────────────
    seasonal = last_ball.groupby(["batter", "season"], as_index=False).agg(
        s_runs  = ("batter_runs", "sum"),
        s_dism  = ("dismissed",   "sum"),
        s_inn   = ("match_id",    "count"),
    )
    seasonal["s_avg"] = np.clip(
    npwhere(
        seasonal["s_dism"] > 0,
        seasonal["s_runs"] / seasonal["s_dism"],
        seasonal["s_runs"] / seasonal["s_inn"].clip(lower=1)
    ),
    a_min=None, a_max=120
)

    seas_stats = seasonal.groupby("batter")["s_avg"].agg(
        avg_of_seasonal_avgs = "mean",
        seasonal_avg_std     = "std",
    ).reset_index()
    seas_stats["seasonal_avg_std"]     = seas_stats["seasonal_avg_std"].fillna(0).round(2)
    seas_stats["avg_of_seasonal_avgs"] = seas_stats["avg_of_seasonal_avgs"].round(2)
    career = career.merge(seas_stats, on="batter", how="left")
    career[["avg_of_seasonal_avgs","seasonal_avg_std"]] = \
        career[["avg_of_seasonal_avgs","seasonal_avg_std"]].fillna(0)

    # ── 3g. Position-adjusted powerplay stats ───────────────────────────────
    pp_df    = bat_df[bat_df["over"] < POWERPLAY_OVERS].copy()
    death_df = bat_df[bat_df["over"] >= DEATH_OVERS_START].copy()

    def phase_stats(phase_df, prefix):
        g = phase_df.groupby("batter", as_index=False).agg(
            **{f"{prefix}_runs":  ("runs_batter",  "sum")},
            **{f"{prefix}_balls": ("valid_ball",    "sum")},
        )
        g[f"{prefix}_sr"] = npwhere(
            g[f"{prefix}_balls"] > 0,
            g[f"{prefix}_runs"] / g[f"{prefix}_balls"] * 100, 0
        ).round(2)
        return g

    pp_stats    = phase_stats(pp_df,    "pp")
    death_stats = phase_stats(death_df, "death")
    career = career.merge(pp_stats,    on="batter", how="left")
    career = career.merge(death_stats, on="batter", how="left")
    for col in ["pp_runs","pp_balls","pp_sr","death_runs","death_balls","death_sr"]:
        career[col] = career[col].fillna(0).round(2)

    # Position-adjusted phase score (0–100, computed later during normalisation)
    # Store the raw values for now; normalise below during GOAT computation.

    # ── 3h. Knockout / Finals stats ─────────────────────────────────────────
    ko_df = last_ball[last_ball["stage"].isin(KNOCKOUT_STAGES)].copy()
    ko_career = ko_df.groupby("batter", as_index=False).agg(
        knockout_innings  = ("match_id",    "count"),
        knockout_runs     = ("batter_runs", "sum"),
        knockout_balls    = ("batter_balls","sum"),
        knockout_dism     = ("dismissed",   "sum"),
        knockout_not_outs = ("dismissed",   lambda x: (x == 0).sum()),
    )
    ko_career["knockout_avg"] = np.clip(
    npwhere(
        ko_career["knockout_dism"] > 0,
        ko_career["knockout_runs"] / ko_career["knockout_dism"],
        ko_career["knockout_runs"] / ko_career["knockout_innings"].clip(lower=1)
    ),
    a_min=None, a_max=120
).round(2)

    ko_career["knockout_sr"] = npwhere(
        ko_career["knockout_balls"] > 0,
        ko_career["knockout_runs"] / ko_career["knockout_balls"] * 100, 0
    ).round(2)
    career = career.merge(ko_career, on="batter", how="left")
    ko_cols = ["knockout_innings","knockout_runs","knockout_balls",
               "knockout_dism","knockout_not_outs","knockout_avg","knockout_sr"]
    career[ko_cols] = career[ko_cols].fillna(0)

    # ── 3i. Seasons list (for display) ───────────────────────────────────────
    seasons_map = (
        last_ball.groupby("batter")["season"]
                 .apply(lambda x: sorted(x.unique().tolist()))
                 .to_dict()
    )
    career["seasons_list"] = career["batter"].map(seasons_map)

    career.rename(columns={"batter": "name"}, inplace=True)
    print(f"   ✓  {len(career):,} batters")
    return career


# ─────────────────────────────────────────────────────────────────────────────
# 4. BUILD BOWLER STATS (basic — GOAT formula TBD)
# ─────────────────────────────────────────────────────────────────────────────

def build_bowler_stats(df):
    """
    Expanded bowler stats — replaces the original basic version.
    Adds seasonal economy, phase splits, and knockout bowling
    needed for the GOAT formula.
    """
    print("🎳  Building bowler stats …")
    bowl_df = df[df["bowler"].notna() & (df["bowler"] != "")].copy()

    # ── Career aggregates ────────────────────────────────────────────────────
    career = bowl_df.groupby("bowler", as_index=False).agg(
        wickets       = ("bowler_wicket", "sum"),
        balls_bowled  = ("valid_ball",    "sum"),
        runs_conceded = ("runs_total",    "sum"),
        matches       = ("match_id",      "nunique"),
        seasons_count = ("season",        "nunique"),
        innings_bowled= ("match_id",      "count"),   # proxy — refined below
    )

    career["economy"] = np.round(npwhere(
        career["balls_bowled"] > 0,
        career["runs_conceded"] / career["balls_bowled"] * 6, 0
    ), 2)

    career["bowling_avg"] = np.round(npwhere(
        career["wickets"] > 0,
        career["runs_conceded"] / career["wickets"], 0
    ), 2)

    career["bowling_sr"] = np.round(npwhere(
        career["wickets"] > 0,
        career["balls_bowled"] / career["wickets"], 0
    ), 2)

    career["wickets_per_match"] = np.round(npwhere(
        career["matches"] > 0,
        career["wickets"] / career["matches"], 0
    ), 2)

    # ── Seasonal economy (for consistency component) ─────────────────────────
    seasonal = bowl_df.groupby(["bowler", "season"], as_index=False).agg(
        s_balls = ("valid_ball",    "sum"),
        s_runs  = ("runs_total",    "sum"),
        s_wkts  = ("bowler_wicket", "sum"),
    )
    seasonal["s_economy"] = npwhere(
        seasonal["s_balls"] > 0,
        seasonal["s_runs"] / seasonal["s_balls"] * 6, 0
    )

    seas_stats = seasonal.groupby("bowler")["s_economy"].agg(
        mean_seasonal_economy = "mean",
        seasonal_economy_std  = "std",
    ).reset_index()
    seas_stats["mean_seasonal_economy"] = seas_stats["mean_seasonal_economy"].round(2)
    seas_stats["seasonal_economy_std"]  = seas_stats["seasonal_economy_std"].fillna(0).round(2)
    career = career.merge(seas_stats, on="bowler", how="left")
    career[["mean_seasonal_economy","seasonal_economy_std"]] = \
        career[["mean_seasonal_economy","seasonal_economy_std"]].fillna(0)

    # ── Phase splits (powerplay / death / middle) ────────────────────────────
    def bowl_phase_stats(phase_df, prefix):
        g = phase_df.groupby("bowler", as_index=False).agg(
            **{f"{prefix}_balls":  ("valid_ball",    "sum")},
            **{f"{prefix}_runs":   ("runs_total",    "sum")},
            **{f"{prefix}_wickets":("bowler_wicket", "sum")},
        )
        g[f"{prefix}_economy"] = np.round(npwhere(
            g[f"{prefix}_balls"] > 0,
            g[f"{prefix}_runs"] / g[f"{prefix}_balls"] * 6, 0
        ), 2)
        g[f"{prefix}_wickets_per_ball"] = np.round(npwhere(
            g[f"{prefix}_balls"] > 0,
            g[f"{prefix}_wickets"] / g[f"{prefix}_balls"], 0
        ), 4)
        return g

    pp_df    = bowl_df[bowl_df["over"] < POWERPLAY_OVERS]
    death_df = bowl_df[bowl_df["over"] >= DEATH_OVERS_START]
    mid_df   = bowl_df[
        (bowl_df["over"] >= POWERPLAY_OVERS) &
        (bowl_df["over"] < DEATH_OVERS_START)
    ]

    pp_stats    = bowl_phase_stats(pp_df,    "pp")
    death_stats = bowl_phase_stats(death_df, "death")
    mid_stats   = bowl_phase_stats(mid_df,   "mid")

    career = career.merge(pp_stats,    on="bowler", how="left")
    career = career.merge(death_stats, on="bowler", how="left")
    career = career.merge(mid_stats,   on="bowler", how="left")

    phase_cols = [
        "pp_balls","pp_runs","pp_wickets","pp_economy","pp_wickets_per_ball",
        "death_balls","death_runs","death_wickets","death_economy","death_wickets_per_ball",
        "mid_balls","mid_runs","mid_wickets","mid_economy","mid_wickets_per_ball",
    ]
    for col in phase_cols:
        if col in career.columns:
            career[col] = career[col].fillna(0)

    # Determine primary bowling role from where most balls bowled
    def bowling_role(row):
        pp    = row.get("pp_balls",    0)
        death = row.get("death_balls", 0)
        mid   = row.get("mid_balls",   0)
        if pp >= death and pp >= mid:
            return "powerplay"
        elif death >= pp and death >= mid:
            return "death"
        else:
            return "middle"

    career["bowling_role"] = career.apply(bowling_role, axis=1)

    # ── Knockout / Finals bowling ────────────────────────────────────────────
    ko_bowl = bowl_df[bowl_df["stage"].isin(KNOCKOUT_STAGES)].copy()

    ko_career = ko_bowl.groupby("bowler", as_index=False).agg(
        knockout_matches  = ("match_id",      "nunique"),
        knockout_balls    = ("valid_ball",     "sum"),
        knockout_runs     = ("runs_total",     "sum"),
        knockout_wickets  = ("bowler_wicket",  "sum"),
    )
    ko_career["knockout_economy"] = np.round(npwhere(
        ko_career["knockout_balls"] > 0,
        ko_career["knockout_runs"] / ko_career["knockout_balls"] * 6, 0
    ), 2)
    ko_career["knockout_wickets_per_match"] = np.round(npwhere(
        ko_career["knockout_matches"] > 0,
        ko_career["knockout_wickets"] / ko_career["knockout_matches"], 0
    ), 2)

    career = career.merge(ko_career, on="bowler", how="left")
    ko_cols = ["knockout_matches","knockout_balls","knockout_runs",
               "knockout_wickets","knockout_economy","knockout_wickets_per_match"]
    career[ko_cols] = career[ko_cols].fillna(0)

    # ── Seasons list ─────────────────────────────────────────────────────────
    seasons_map = (
        bowl_df.groupby("bowler")["season"]
               .apply(lambda x: sorted(x.unique().tolist()))
               .to_dict()
    )
    career["seasons_list"] = career["bowler"].map(seasons_map)

    career.rename(columns={"bowler": "name"}, inplace=True)
    print(f"   ✓  {len(career):,} bowlers")
    return career


# ─────────────────────────────────────────────────────────────────────────────

def compute_bowler_goat(bowler_df):
    """
    Adds bowler_goat_score + bowler_goat_breakdown to bowler_df.
    Only players with matches >= BOWLER_MIN_MATCHES
    AND wickets >= BOWLER_MIN_WICKETS qualify.
    """
    print("🏆  Computing bowler GOAT scores …")

    df = bowler_df.copy()
    q  = df[
        (df["matches"]  >= BOWLER_MIN_MATCHES) &
        (df["wickets"]  >= BOWLER_MIN_WICKETS)
    ].copy()

    # ── Component 1: Wicket Taking Ability (30%) ─────────────────────────────
    # wickets_per_match (frequency) + inverted bowling_sr (speed of taking wickets)
    # bowling_sr = balls per wicket — lower is better → invert
    q["_bsr_inv"] = 100 - minmax(q["bowling_sr"].clip(upper=60))
    q["_c1"] = (
        0.50 * minmax(q["wickets_per_match"]) +
        0.50 * q["_bsr_inv"]
    )

    # ── Component 2: Economy & Pressure (20%) ────────────────────────────────
    # mean_seasonal_economy with std penalty — lower economy = better → invert
    # consistency_raw = mean_eco + 0.3*std (higher = worse), then invert
    q["_eco_consistency_raw"] = (
        q["mean_seasonal_economy"] + 0.3 * q["seasonal_economy_std"]
    ).clip(upper=12)
    q["_c2"] = 100 - minmax(q["_eco_consistency_raw"])

    # ── Component 3: Impact Moments (25%) ────────────────────────────────────
    # knockout wickets per match (60%) + inverted knockout economy (40%)
    # players with 0 knockout matches get 0 — fair
    q["_ko_eco_inv"] = npwhere(
        q["knockout_matches"] > 0,
        100 - minmax(q["knockout_economy"].clip(upper=15)),
        0
    )
    q["_ko_confidence"] = (q["knockout_matches"] / 8).clip(upper=1.0)
    q["_impact_raw"] = (
    0.60 * minmax(q["knockout_wickets_per_match"]) +
    0.40 * q["_ko_eco_inv"]
    )
    q["_c3"] = q["_impact_raw"] * q["_ko_confidence"]  # ← apply it here

    # ── Component 4: Phase Bowling (15%) ─────────────────────────────────────
    # Uses bowling_role to pick the right phase stats per bowler
    # Score = wickets_per_ball in their primary phase (normalized)
    #       + inverted economy in their primary phase
    def phase_score(row):
        role = row["bowling_role"]
        if role == "powerplay":
            wpb = row["pp_wickets_per_ball"]
            eco = row["pp_economy"]
        elif role == "death":
            wpb = row["death_wickets_per_ball"]
            eco = row["death_economy"]
        else:
            wpb = row["mid_wickets_per_ball"]
            eco = row["mid_economy"]
        return wpb, eco

    q[["_phase_wpb","_phase_eco"]] = q.apply(
        phase_score, axis=1, result_type="expand"
    )
    q["_c4"] = (
        0.55 * minmax(q["_phase_wpb"]) +
        0.45 * (100 - minmax(q["_phase_eco"].clip(upper=15)))
    )

    # ── Component 5: Longevity (10%) ─────────────────────────────────────────
    q["_c5"] = (
        0.50 * minmax(q["seasons_count"]) +
        0.50 * minmax(q["matches"])
    )

    # ── Weighted GOAT score ──────────────────────────────────────────────────
    q["_career_maturity"] = (q["matches"] / 60).clip(upper=1.0)
    q["bowler_goat_score"] = (
        GOAT_WEIGHTS_BOWLER["wicket_taking"]  * q["_c1"] +
        GOAT_WEIGHTS_BOWLER["economy"]        * q["_c2"] +
        GOAT_WEIGHTS_BOWLER["impact_moments"] * q["_c3"] +
        GOAT_WEIGHTS_BOWLER["phase_bowling"]  * q["_c4"] +
        GOAT_WEIGHTS_BOWLER["longevity"]      * q["_c5"]
    )* q["_career_maturity"]

    # ── Breakdown dict ───────────────────────────────────────────────────────
    q["bowler_goat_breakdown"] = q.apply(lambda r: {
        "wicket_taking":  round(r["_c1"], 2),
        "economy":        round(r["_c2"], 2),
        "impact_moments": round(r["_c3"], 2),
        "phase_bowling":  round(r["_c4"], 2),
        "longevity":      round(r["_c5"], 2),
    }, axis=1)

    # Drop temp cols
    temp_cols = [c for c in q.columns if c.startswith("_")]
    q.drop(columns=temp_cols, inplace=True)

    # Merge back — non-qualifiers get 0
    df = df.merge(
        q[["name","bowler_goat_score","bowler_goat_breakdown"]],
        on="name", how="left"
    )
    df["bowler_goat_score"] = df["bowler_goat_score"].fillna(0).round(2)
    df["bowler_goat_breakdown"] = df["bowler_goat_breakdown"].apply(
        lambda x: x if isinstance(x, dict) else {}
    )

    print(f"   ✓  GOAT scores computed for {len(q)} qualifying bowlers")
    return df

# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPUTE BATTER GOAT SCORES
# ─────────────────────────────────────────────────────────────────────────────

def compute_batter_goat(batter_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds batter_goat_score + batter_goat_breakdown to batter_df.
    Only players with matches >= MIN_MATCHES get a non-zero GOAT score.
    Normalisation is done ACROSS the qualifying pool only.
    """
    print("🏆  Computing batter GOAT scores …")

    df = batter_df.copy()
    q  = df[df["matches"] >= MIN_MATCHES].copy()   # qualifying pool

    # ── Component 1: Volume & Dominance (25%) ───────────────────────────────
    # runs_contribution_pct already captures runs / team_runs_while_batting
    q["_c1"] = minmax(q["runs_contribution_pct"])

    # ── Component 2: Consistency (20%) ──────────────────────────────────────
    # Mean of per-season batting averages — rewards sustained excellence
    # Penalise high std (inconsistency): consistency = avg_of_seas_avgs - 0.3*std
    q["_consistency_raw"] = (
        q["avg_of_seasonal_avgs"] - 0.3 * q["seasonal_avg_std"]
    ).clip(lower=0)
    q["_c2"] = minmax(q["_consistency_raw"])

    # ── Component 3: Impact Moments (25%) ───────────────────────────────────
    # Batting avg in knockouts (60%) + SR in knockouts (20%) + not-out bonus (20%)
    q["_ko_not_out_rate"] = npwhere(
        q["knockout_innings"] > 0,
        q["knockout_not_outs"] / q["knockout_innings"] * 100, 0
    )
    q["_impact_raw"] = (
        0.60 * minmax(q["knockout_avg"].clip(upper=100)) +
        0.20 * minmax(q["knockout_sr"].clip(upper=250)) +
        0.20 * minmax(q["_ko_not_out_rate"])
    )
    # Players with 0 knockout innings get impact = 0 (fair — they never played knockouts)
    q["_ko_confidence"] = (q["knockout_innings"] / 10).clip(upper=1.0)

    q["_impact_raw"] = (
    0.60 * minmax(q["knockout_avg"].clip(upper=100)) +
    0.20 * minmax(q["knockout_sr"].clip(upper=250)) +
    0.20 * minmax(q["_ko_not_out_rate"])
    )

    # Apply confidence scaling — Tiwary's 1 innings gets ~10% weight, Dhoni's 33 gets 100%
    q["_c3"] = q["_impact_raw"] * q["_ko_confidence"]

    # ── Component 4: Boundary Aggression (15%) ──────────────────────────────
    q["_c4"] = (
        0.60 * minmax(q["boundary_pct"]) +
        0.40 * minmax(q["six_rate"])
    )

    # ── Component 5: Career Longevity (15%) ─────────────────────────────────
    q["_c5"] = (
        0.50 * minmax(q["seasons_count"]) +
        0.50 * minmax(q["matches"])
    )

    # ── Position-adjusted powerplay modifier ────────────────────────────────
    # This adjusts Component 3 (impact) slightly — openers get pp_sr factored in,
    # finishers get death_sr. Applied as a +/- modifier (±10% of Component 4).
    def phase_modifier(row):
        pos = row["bat_pos_mode"]
        if pos in OPENER_POSITIONS:
            # opener: normalise pp_sr (done later, use raw ratio here)
            return row["pp_sr"]
        elif pos in FINISHER_POS:
            return row["death_sr"]
        else:
            # mid-order: blend pp and death evenly
            return 0.5 * row["pp_sr"] + 0.5 * row["death_sr"]

    q["_phase_raw"] = q.apply(phase_modifier, axis=1)
    q["_phase_norm"] = minmax(q["_phase_raw"])
    # Blend phase performance into boundary aggression component (it's also attack)
    q["_c4_adj"] = 0.70 * q["_c4"] + 0.30 * q["_phase_norm"]
    q["_career_maturity"] = (q["matches"] / 80).clip(upper=1.0)

    # ── Weighted GOAT score ──────────────────────────────────────────────────
    q["batter_goat_score"] = (
        GOAT_WEIGHTS["volume_dominance"]    * q["_c1"] +
        GOAT_WEIGHTS["consistency"]         * q["_c2"] +
        GOAT_WEIGHTS["impact_moments"]      * q["_c3"] +
        GOAT_WEIGHTS["boundary_aggression"] * q["_c4_adj"] +
        GOAT_WEIGHTS["longevity"]           * q["_c5"]
    )* q["_career_maturity"]

    # ── Breakdown dict (for API response) ───────────────────────────────────
    q["batter_goat_breakdown"] = q.apply(lambda r: {
        "volume_dominance":    round(r["_c1"],      2),
        "consistency":         round(r["_c2"],      2),
        "impact_moments":      round(r["_c3"],      2),
        "boundary_aggression": round(r["_c4_adj"],  2),
        "longevity":           round(r["_c5"],      2),
    }, axis=1)

    # Drop temp columns
    temp_cols = [c for c in q.columns if c.startswith("_")]
    q.drop(columns=temp_cols, inplace=True)

    # Merge back into full df (non-qualifying players get NaN → filled below)
    df = df.merge(
        q[["name","batter_goat_score","batter_goat_breakdown"]],
        on="name", how="left"
    )
    df["batter_goat_score"] = df["batter_goat_score"].fillna(0).round(2)
    df["batter_goat_breakdown"] = df["batter_goat_breakdown"].apply(
        lambda x: x if isinstance(x, dict) else {}
    )
    print(f"   ✓  GOAT scores computed for {len(q)} qualifying batters")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 6. MERGE & SERIALISE players.json
# ─────────────────────────────────────────────────────────────────────────────

def build_players_json(df):
    print("🔀  Merging batter + bowler stats …")
    batter_stats = build_batter_stats(df)
    batter_stats = compute_batter_goat(batter_stats)
    bowler_stats = build_bowler_stats(df)
    bowler_stats = compute_bowler_goat(bowler_stats)

    merged = pd.merge(batter_stats, bowler_stats, on="name", how="outer",
                      suffixes=("", "_bowl"))

    # Resolve matches / seasons from either side
    merged["matches"] = merged["matches"].combine_first(merged.get("matches_bowl")).fillna(0)
    if "seasons_count_bowl" in merged.columns:
        merged["seasons_count"] = merged["seasons_count"].combine_first(
            merged["seasons_count_bowl"]
        ).fillna(0)

    # Fill numeric NaNs
    num_cols = merged.select_dtypes(include=[np.number]).columns
    merged[num_cols] = merged[num_cols].fillna(0)

    # Round floats to 2 dp
    float_cols = merged.select_dtypes(include=[float]).columns
    merged[float_cols] = merged[float_cols].round(2)

    # Drop redundant suffixed columns
    drop = [c for c in merged.columns if c.endswith("_bowl")]
    merged.drop(columns=drop, inplace=True, errors="ignore")

    # Convert to int where appropriate
    int_cols = ["matches","innings","dismissals","not_outs","fours","sixes",
                "total_runs","total_balls","seasons_count","wickets",
                "balls_bowled","runs_conceded","boundary_runs",
                "pp_runs","pp_balls","death_runs","death_balls",
                "knockout_runs","knockout_balls","knockout_innings",
                "knockout_dism","knockout_not_outs"]
    for col in int_cols:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0).astype(int)

    # seasons_list: ensure JSON-serialisable list
    if "seasons_list" in merged.columns:
        merged["seasons_list"] = merged["seasons_list"].apply(
            lambda x: x if isinstance(x, list) else []
        )

    # batter_goat_breakdown: ensure dict
    merged["batter_goat_breakdown"] = merged["batter_goat_breakdown"].apply(
        lambda x: x if isinstance(x, dict) else {}
    )
    merged["bowler_goat_breakdown"] = merged["bowler_goat_breakdown"].apply(
    lambda x: x if isinstance(x, dict) else {}
    
)

    records = merged.to_dict(orient="records")
    merged["bowling_role"] = merged["bowling_role"].fillna("N/A")

    out_path = os.path.join(OUT_DIR, "players.json")
    with open(out_path, "w") as f:
        json.dump(records, f, separators=(",", ":"), default=str)
    print(f"   ✓  players.json  →  {len(records):,} players  ({_fsize(out_path)})")




# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _fsize(path):
    size = os.path.getsize(path)
    if size < 1024:       return f"{size} B"
    if size < 1024**2:    return f"{size/1024:.1f} KB"
    return f"{size/1024**2:.2f} MB"


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def run():
    print("\n" + "="*60)
    print("  IPL Dashboard — Preprocessing Pipeline")
    print("="*60 + "\n")

    df = load_data()

    # ✅ New — enriched players + GOAT scores
    build_players_json(df)

    print("\n" + "="*60)
    print("  ✅  Done")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()


if __name__ == "__main__":
    run()