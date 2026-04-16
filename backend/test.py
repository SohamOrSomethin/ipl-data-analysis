import sys
import statistics
sys.path.insert(0, '.')

from app import (
    get_pair_matches_before, get_recent_form, get_venue_winpct,
    get_current_season_form,
    get_home_boost, get_toss_score, resolve_team, normalise_venue,
    MATCH_SUMMARY
)

WEIGHTS = {
    "h2h":   0.10,   # slash — it's noise
    "form":  0.10,   # slash — it's anti-signal
    "venue": 0.40,   # most stable long-term signal
    "home":  0.25,   # reliable structural advantage
    "toss":  0.15,   # small but consistent
}
debug_scores = []

TEST_SEASONS = ["2023", "2024", "2025"]


def predict(team1, team2, venue, toss_winner, toss_decision, match_date):
    # ── H2H (last 4 seasons only) ────────────────────────────────────────────
    pair_matches = get_pair_matches_before(team1, team2, before_date=match_date)
    
    # ← ADD THIS: only use H2H from last 4 seasons
    current_year = int(match_date[:4])
    pair_matches = [
        m for m in pair_matches
        if int(m.get("season", 0)) >= current_year - 4
    ]
    
    decided = [m for m in pair_matches if m.get("winner") in [team1, team2]]
    t1_wins = sum(1 for m in decided if m["winner"] == team1)
    h2h_t1 = round(t1_wins / len(decided) * 100, 2) if decided else 50.0
    h2h_t2 = round(100 - h2h_t1, 2)

    # ── Form ─────────────────────────────────────────────────────────────────
    form_t1 = get_current_season_form(team1,current_season=current_year, before_date=match_date)
    form_t2 = get_current_season_form(team2,current_season=current_year,before_date=match_date)

    # ── Venue ────────────────────────────────────────────────────────────────
    venue_t1 = get_venue_winpct(team1, venue, before_date=match_date)
    venue_t2 = get_venue_winpct(team2, venue, before_date=match_date)

    # ── Home (static, no date needed) ────────────────────────────────────────
    home_t1 = get_home_boost(team1, venue)
    home_t2 = get_home_boost(team2, venue)

    # ── Toss (venue tendency is fine all-time) ───────────────────────────────
    toss_t1 = get_toss_score(toss_winner, team1, toss_decision, venue)
    toss_t2 = get_toss_score(toss_winner, team2, toss_decision, venue)

    # ── Weighted score ───────────────────────────────────────────────────────
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

    total = raw_t1 + raw_t2
    win_pct_t1 = raw_t1 / total * 100 if total > 0 else 50.0
    return team1 if win_pct_t1 >= 50 else team2


# ── Backtest loop ────────────────────────────────────────────────────────────
correct = 0
total = 0
wrong_matches = []
season_stats = {s: {"correct": 0, "total": 0} for s in TEST_SEASONS}
debug_scores = []  # ← new

for m in MATCH_SUMMARY:
    season = str(m.get("season", ""))
    if season not in TEST_SEASONS:
        continue
    if m.get("result") != "completed":
        continue
    if not m.get("winner"):
        continue

    match_date    = m.get("date", "")
    team1         = resolve_team(m["team1"])
    team2         = resolve_team(m["team2"])
    venue         = normalise_venue(m.get("venue", ""))
    toss_winner   = resolve_team(m.get("toss_winner", ""))
    toss_decision = m.get("toss_decision", "")
    actual_winner = resolve_team(m["winner"])

    # ── Compute all scores individually (needed for debug) ───────────────
    pair_matches = get_pair_matches_before(team1, team2, before_date=match_date)
    current_year = int(match_date[:4])
    pair_matches = [m2 for m2 in pair_matches if int(m2.get("season", 0)) >= current_year - 4]
    decided = [m2 for m2 in pair_matches if m2.get("winner") in [team1, team2]]
    t1_wins = sum(1 for m2 in decided if m2["winner"] == team1)
    h2h_t1 = round(t1_wins / len(decided) * 100, 2) if decided else 50.0
    h2h_t2 = round(100 - h2h_t1, 2)

    form_t1  = get_current_season_form(team1,current_season=current_year,before_date=match_date)
    form_t2  = get_current_season_form(team2,current_season=current_year,before_date=match_date)
    venue_t1 = get_venue_winpct(team1, venue, before_date=match_date)
    venue_t2 = get_venue_winpct(team2, venue, before_date=match_date)
    home_t1  = get_home_boost(team1, venue)
    home_t2  = get_home_boost(team2, venue)
    toss_t1  = get_toss_score(toss_winner, team1, toss_decision, venue)
    toss_t2  = get_toss_score(toss_winner, team2, toss_decision, venue)

    raw_t1 = (WEIGHTS["h2h"] * h2h_t1 + WEIGHTS["form"] * form_t1 +
              WEIGHTS["venue"] * venue_t1 + WEIGHTS["home"] * home_t1 +
              WEIGHTS["toss"] * toss_t1)
    raw_t2 = (WEIGHTS["h2h"] * h2h_t2 + WEIGHTS["form"] * form_t2 +
              WEIGHTS["venue"] * venue_t2 + WEIGHTS["home"] * home_t2 +
              WEIGHTS["toss"] * toss_t2)

    total_score = raw_t1 + raw_t2
    win_pct_t1 = raw_t1 / total_score * 100 if total_score > 0 else 50.0
    predicted = team1 if win_pct_t1 >= 50 else team2

    # ── Debug capture ────────────────────────────────────────────────────
    debug_scores.append({
        "h2h":    round(abs(h2h_t1 - 50), 1),
        "form":   round(abs(form_t1 - 50), 1),
        "venue":  round(abs(venue_t1 - 50), 1),
        "home":   round(abs(home_t1 - 50), 1),
        "toss":   round(abs(toss_t1 - 50), 1),
        "margin": round(abs(win_pct_t1 - 50), 1),
        "correct": predicted == actual_winner
    })

    total += 1
    season_stats[season]["total"] += 1

    if predicted == actual_winner:
        correct += 1
        season_stats[season]["correct"] += 1
    else:
        wrong_matches.append({
            "season":    season,
            "date":      match_date,
            "match":     f"{team1} vs {team2}",
            "predicted": predicted,
            "actual":    actual_winner,
            "venue":     venue,
        })

# ── Results ──────────────────────────────────────────────────────────────────
accuracy = round(correct / total * 100, 2) if total else 0

print(f"\n📊 Backtest Results — Seasons: {', '.join(TEST_SEASONS)}")
print(f"   Total matches : {total}")
print(f"   Correct       : {correct}")
print(f"   Accuracy      : {accuracy}%")

print(f"\n📅 Per-season breakdown:")
for s, stats in season_stats.items():
    s_acc = round(stats["correct"] / stats["total"] * 100, 2) if stats["total"] else 0
    print(f"   {s} → {stats['correct']}/{stats['total']} = {s_acc}%")

print(f"\n📐 Average signal strength per factor (higher = more decisive input):")
for factor in ["h2h", "form", "venue", "home", "toss"]:
    vals = [d[factor] for d in debug_scores]
    avg = round(statistics.mean(vals), 2)
    # accuracy when this factor was the strongest signal
    print(f"   {factor:6} → avg deviation from 50: {avg}")

avg_margin = round(statistics.mean(d["margin"] for d in debug_scores), 2)
coin_flips = round(sum(1 for d in debug_scores if d["margin"] < 2) / len(debug_scores) * 100, 1)
print(f"\n   avg prediction margin : {avg_margin}")
print(f"   coin-flip matches (<2% margin) : {coin_flips}%")

print(f"\n❌ Wrong predictions ({len(wrong_matches)}):")
for w in wrong_matches[:15]:
    print(f"   {w['date']} | {w['match']} @ {w['venue']}")
    print(f"   → predicted: {w['predicted']} | actual: {w['actual']}")