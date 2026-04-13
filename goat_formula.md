# IPL GOAT Scoring Formula

This document explains how the GOAT (Greatest of All Time) scores are calculated
for batters and bowlers in the IPL Stats Dashboard.

All scores are normalised to **0–100** using min-max normalisation across
the qualifying player pool. The player with the best raw value in any component
gets 100, the worst gets 0, everyone else scales in between.

---

## Batter GOAT Score

**Minimum qualification:** 20 matches played

| Component | Weight | What it measures |
|---|---|---|
| Volume & Dominance | 25% | Share of team runs scored while batting |
| Consistency | 20% | Seasonal average stability across career |
| Impact Moments | 25% | Performance in finals and knockouts |
| Boundary Aggression | 15% | Explosive scoring + phase-adjusted SR |
| Career Longevity | 15% | Seasons played + total matches |

### Component Breakdown

**1. Volume & Dominance (25%)**
- `runs_contribution_pct = player_runs / team_total_runs_in_innings_played × 100`
- team_total_runs_in_innings_played = sum of all runs scored by the team
in every innings where this player batted.
Expected range: 15–30% (normal), 30%+ (very dominant)`
- Measures batting *importance* not just volume — a player scoring 40/120 ranks
  higher than one scoring 60/220 on this metric

**2. Consistency (20%)**
- Batting average is computed *per season*, not as a career total
- Final score = mean of seasonal averages − (0.3 × standard deviation)
- The std penalty rewards players who perform well every season over
  one-season wonders with a single massive average

**3. Impact Moments (25%)**
- Only matches with stage = final / qualifier 1 / qualifier 2 / eliminator count
- Score = 60% knockout batting average + 20% knockout strike rate + 20% not-out rate in knockouts
- Not-out rate bonus rewards match-finishers (Dhoni-style)
- Players who never appeared in a knockout get 0 on this component
- A confidence weight is applied to prevent small sample bias:  weight = min(1.0, knockout_innings / 10)

**4. Boundary Aggression + Phase Bonus (15%)**
- Base = 60% boundary% (runs from 4s and 6s / total runs) + 40% six rate (sixes per 100 balls)
- Phase bonus uses batting position (bat_pos) to pick the right phase:
  - Position 1–2 (openers) → powerplay strike rate (overs 1–6)
  - Position 5–8 (finishers) → death overs strike rate (overs 16–20)
  - Position 3–4 (middle order) → 50/50 blend of both
- Final = 70% base aggression + 30% phase bonus

**5. Career Longevity (15%)**
- 50% unique seasons played + 50% total matches played
- Both signals combined prevent gaming — seasons alone rewards 1-match-per-season
  appearances; matches alone rewards a player who played 80 games then retired early

### Final Formula
```
GOAT_batter = (0.25 × C1) + (0.20 × C2) + (0.25 × C3) + (0.15 × C4) + (0.15 × C5)
```

---

## Bowler GOAT Score

**Minimum qualification:** 20 matches played AND 15 wickets taken

> Key difference from batter formula: economy rate and bowling strike rate are
> "lower is better" metrics, so their normalisation is inverted (100 − norm).

| Component | Weight | What it measures |
|---|---|---|
| Wicket Taking Ability | 30% | Frequency and speed of taking wickets |
| Economy & Pressure | 20% | Consistently hard to score off across seasons |
| Impact Moments | 25% | Wickets and economy in finals and knockouts |
| Phase Bowling | 15% | Dominance in their specialist phase |
| Career Longevity | 10% | Seasons played + total matches |

### Component Breakdown

**1. Wicket Taking Ability (30%)**
- 50% wickets per match (frequency)
- 50% inverted bowling strike rate — balls per wicket, lower is better
- Bowling SR capped at 60 before normalisation to prevent outliers

**2. Economy & Pressure (20%)**
- Economy rate computed per season
- Consistency raw = mean seasonal economy + (0.3 × std deviation)
- The std penalty is added (not subtracted) because higher economy = worse
- Final score is inverted: 100 − norm, so lower economy = higher score

**3. Impact Moments (25%)**
- Only finals and knockout matches count
- Score = 60% knockout wickets per match + 40% inverted knockout economy
- Players who never appeared in a knockout get 0 on this component
- A confidence weight is applied to prevent small sample bias: weight = min(1.0, knockout_matches / 8)

**4. Phase Bowling (15%)**
- Each bowler's primary role is determined by where they bowl the most balls:
  - Most balls in overs 1–6 → powerplay specialist
  - Most balls in overs 16–20 → death bowling specialist
  - Otherwise → middle overs specialist
- Score = 55% wickets per ball in their phase + 45% inverted economy in their phase
- Wickets per ball weighted slightly higher because taking wickets in your
  specialist phase is the ultimate T20 differentiator

**5. Career Longevity (10%)**
- Same formula as batters: 50% seasons + 50% matches
- Weighted lower (10% vs 15%) because bowling careers are shorter and
  more injury-prone — prime-career specialists should not be penalised

### Final Formula
```
GOAT_bowler = (0.30 × C1) + (0.20 × C2) + (0.25 × C3) + (0.15 × C4) + (0.10 × C5)
```

---
## Score Adjustments

### Career Maturity Penalty
Applied as a multiplier to the final GOAT score before re-normalisation.

- Batters:  multiplier = min(1.0, matches / 80)
  - 80+ matches → full score
  - 20 matches (minimum) → 25% of score
- Bowlers:  not currently applied (minimum thresholds handle this)

This prevents short-career players from ranking above legends purely
on rate stats with a small sample size.

### Re-normalisation
After all scores are computed across the qualifying pool, a final
min-max re-normalisation is applied so scores always span 0–100.
The best player in the qualifying pool always scores 100.

## API

```
GET /api/goat              → top 10 batters (default)
GET /api/goat?role=batter  → top 10 batters
GET /api/goat?role=bowler  → top 10 bowlers
GET /api/goat?limit=25     → up to 25 results
```

Each player in the response includes their full score breakdown so the
frontend can render a radar/bar chart showing all 5 components.

---

## Design Decisions

- Scores are pre-computed at startup via `preprocess.py` and cached in
  `players.json` — the API endpoint does zero CSV scanning
- Min-max normalisation is computed across the qualifying pool only,
  so non-qualifying players (score = 0) do not distort the scale
- Bowler and batter GOAT scores are completely independent — an allrounder
  will have both a `batter_goat_score` and a `bowler_goat_score`
