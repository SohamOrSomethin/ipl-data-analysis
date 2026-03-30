#  IPL Stats Dashboard

A full-stack cricket analytics web app built with **Flask + React**, powered by ball-by-ball IPL match data.

---

## Tech Stack

| Layer    | Technology               |
|----------|--------------------------|
| Backend  | Python, Flask, Pandas    |
| Frontend | React, Axios             |
| Data     | IPL ball-by-ball CSV     |
| Cache    | Static JSON files        |

---

## Project Structure

```
ipl-dashboard/
├── app.py                 # Flask backend
├── export_data.py          # Generates static JSON files from CSV
├── data/
│   └── ipl_data.csv       # Raw ball-by-ball IPL  data
├── static/
│   └── data/
│       ├── players.json   # Pre-built career stats (all players)
│       └── seasons.json   # List of available seasons
└── client/                # React frontend
    ├── src/
    │   ├── App.jsx
    │   └── components/
    └── package.json
```
## Installation

### 1. Clone the repository

```bash
git clone (this repo)
cd ipl-dashboard
```

### 2. Set up Python environment

```bash
python -m venv venv
venv\Scripts\activate
pip install flask pandas flask-cors
```

### 3. Add the dataset

Place your IPL ball-by-ball CSV file at: data/ipl_data.csv

### 4. Generate static JSON files

Run this once before starting the server (and again whenever the dataset changes):

```bash
python export_data.py
```
Server runs at `http://localhost:5000`

### 5. Start the React frontend

```bash
cd client
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## API Endpoints

### `GET /api/players`

Search for players by name. Supports optional season filtering.

**Query Parameters**

| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| `name`    | string | Yes      | Player name (min 2 characters)       |
| `season`  | string | No       | Filter by season (e.g. `2023`). Omit for all-time stats |

**Example Requests**
GET /api/players?name=Kohli
GET /api/players?name=Kohli&season=2023
GET /api/players?name=Bumrah&season=2022

**Example Response**

```json
[
  {
    "name": "V Kohli",
    "runs": 892,
    "balls_faced": 634,
    "fours": 78,
    "sixes": 22,
    "wickets": 0
  }
]
```

---
## Features

- **Player search** — Live search by name with 2-character minimum
- **Batting stats** — Runs, balls faced, 4s, 6s, strike rate
- **Bowling stats** — Total wickets taken
- **Season filter** — View stats for a specific IPL season or all-time
- **Smart data strategy** — All-time queries use pre-built JSON cache; season-filtered queries scan the CSV for accuracy
- **Dual-source player lookup** — Searches both `batter` and `bowler` columns, so all-rounders and pure bowlers are included

---
## Data Notes

- `players.json` is generated from the full CSV at startup via `preprocess.py`
- Season-filtered requests (`?season=XXXX`) always query the live CSV for correctness
- All numeric fields are returned as integers; `strike_rate` is a float rounded to 2 decimal places
- Players with 0 batting or 0 bowling appearances are still included via outer join

---
