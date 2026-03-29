# IPL 2008–2025 Data Analysis

Jupyter notebook for analyzing IPL ball‑by‑ball data (2008–2025), including:
- Top run‑scorers
- Most sixes and fours
- Most wickets
- Team‑wise stats

---

## 1. Prerequisites

You need:
- Python 3.11.9 (create virtual environment)
- node installed


Install dependencies:

```bash
pip install pandas numpy flask flask-cors
```

## 2. steps

- i. run flask server in one terminal
- ii. in another terminal npm intall axios recharts
- iii. npm run dev

### 3. what works

- saare links in flask wala file
- also stuff like http://localhost:5000/api/top-batters?season=2023  if you add ?season="Season" vo automatic filter karega
- frontend pe top batsmen and bowlers for each season can filter by year
- purple and orange cap each year
