# IPL Data Analytics Platform

A high-performance, full-stack cricket analytics dashboard visualizing ball-by-ball performance data from the Indian Premier League (IPL). Built with a **Flask API**, a stunning **React + Vite** frontend, and optimized with a blitz-fast **Static JSON** distribution layer.

---

## Architecture Stack

| Layer    | Technology               | Purpose |
|----------|--------------------------|---------|
| **Backend**  | Python, Flask, Pandas | Parsers and APIs for handling heavy data logic on the raw CSV data. |
| **Frontend** | React, Vite, CSS, Recharts | Premium, responsive visual UI featuring a "Night Match" dark mode. |
| **Delivery** | Static JSONs | Blazing fast local/Vercel delivery for All-Time statistics routing. |

---

## Project Structure

```text
ipl-data-analysis/
├── backend/               # Flask Python Server
│   ├── app.py             # Main routing and dynamic queries
│   ├── export_data.py     # Batch processor: CSV -> Static JSONs
│   ├── static/data/       # Generated data dumps
│   └── ...
├── data/
│   └── IPL.csv            # Original ball-by-ball dataset (Kaggle)
├── frontend/              # React Vite Application
│   ├── public/data/       # Frontend-static dataset copies (fast-path routing)
│   ├── src/
│   │   ├── pages/         # OrangeCap, PurpleCap, Analytics Panels
│   │   ├── index.css      # Custom premium glassmorphic styling
│   │   └── App.jsx
│   └── package.json
└── readme.md
```

---

## Quick Start

### 1. Setup Backend (Data & API)

Ensure the massive IPL ball-by-ball CSV is located at `data/IPL.csv`. Next, activate your python environment and generate the Static Models:

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Or `source venv/bin/activate` 
pip install -r requirements.txt  # Or manually install flask pandas flask-cors

# 1. Regenerate optimized JSONs from CSV
python export_data.py

# 2. Boot up the dynamic API router
python app.py
```
*Backend runs locally at `http://localhost:5000`*


### 2. Setup Frontend

Because of the Static File linkage, you'll need the JSONs copied into `/frontend/public/data/` if they aren't already.

```bash
cd frontend
npm install

# Start the blazingly fast development server
npm run dev
```
*Frontend interface accessible at `http://localhost:5173`*

---

## Smart Data Strategy

This platform uses a duel-resolution data approach:

1. **Lightning Fast "All-Time" Queries:** The Vite client will organically poll `/data/...` pre-built caches instead of waking up your Python deployment, rendering complex graphs instantly.
2. **Dynamic "Season-Filtered" Queries:** When digging deep into specific seasons (e.g. "Who was the best bowler in 2023?"), React cascades requests down via Axios to the Python Flask backend to run a parameterized Pandas dataframe scan over the raw CSV.

---

## Features Included

- **Leaderboards:** Track all-time highest scorers and top wicket-takers through interactive, responsive Data Visualizations (powered by `Recharts`).
- **Award Caches:** Beautiful data-tables dynamically highlighting the Orange Cap and Purple Cap receivers through history.
- **Premium UI:** Entire client stylized with modern "Night Match" glassmorphism, completely devoid of heavy CSS frameworks for maximal performance and customized theming.
