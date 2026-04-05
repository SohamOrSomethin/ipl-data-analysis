# IPL Data Analytics Platform

A high-performance, full-stack cricket analytics dashboard visualizing ball-by-ball performance data from the Indian Premier League (IPL). This platform provides deep insights into player performances, team trends, and historical records with a premium, glassmorphic UI.

---

## 🚀 Key Features

- **🏆 Dynamic Leaderboards:** Track top 10 batters (runs) and bowlers (wickets) with season-specific filtering or all-time aggregated views.
- **🛡️ Team Analytics Dashboard:** Comprehensive view of franchise performance, including:
  - Total Wins, Matches Played, and Win Percentage.
  - **Net Run Rate (NRR)** calculations.
  - **Home vs Away** match distribution analysis.
  - **Season History:** Win/Loss trends over the years.
  - **Key Performers:** Automated identification of a team's top 3 batters and bowlers.
- **👤 Advanced Player Search:** Instant search for over 600+ IPL players with detailed career statistics including runs, balls faced, strike rates, 4s, 6s, and wickets.
- **⚔️ Head-to-Head (Rivalry):** Directly compare the historical performance of any two franchises to see win/loss distributions, total matches, and win rates.
- **🏆 All-Time Records Wall:** Visually engaging cards detailing the highest team totals, lowest scores, and best individual batting and bowling figures in IPL history.
- **🥇 Award Histories:** Interactive tables for **Orange Cap** and **Purple Cap** winners across all IPL seasons.
- **🎨 Premium "Night Match" UI:** A custom-styled glassmorphic interface designed for clarity and visual impact, optimized for large data visualizations using `Recharts`.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite, Recharts, Axios | Responsive UI, high-speed rendering, and interactive data viz. |
| **Backend** | Python, Flask, Pandas | Heavy-lift data processing, normalization, and dynamic API endpoints. |
| **Styling** | Vanilla CSS (Glassmorphism) | Lightweight, performant, and premium design language. |
| **Data Flow** | Hybrid Static/Dynamic | Pre-generated caches for global stats + live Pandas queries for filters. |

---

## 📂 Project Structure

```text
ipl-data-analysis/
├── backend/               # Flask Application
│   ├── app.py             # Main API & Routing logic
│   ├── export_data.py     # Batch Data Pre-processor (CSV -> JSON)
│   └── static/data/       # Optimized data caches for heavy queries
├── data/
│   └── IPL.csv            # Original ball-by-ball dataset (Kaggle)
├── frontend/              # Vite + React Application
│   ├── src/
│   │   ├── pages/         # Dashboard, TeamSelector, Players, etc.
│   │   ├── components/    # Reusable UI elements
│   │   ├── App.jsx        # Routing and Page layout
│   │   └── index.css      # Core Design System
│   └── public/data/       # Static assets for instant load-path
└── README.md
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.9+ 
- Node.js 18+
- The `IPL.csv` dataset placed in the `/data/` folder.

### 2. Setup Backend (Data & API)

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# 1. First, generate the optimized statistics caches
python export_data.py

# 2. Start the API server
python app.py
```
*Backend runs at `http://localhost:5000`*

### 3. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```
*Frontend runs at `http://localhost:5173`*

---

## 📊 Data Strategy

This platform uses a **dual-resolution architecture** to ensure performance:
1. **Cache Layer:** Pre-calculated JSON files for all-time stats (Orange Cap, Purple Cap, Player listings) allow for sub-100ms initial page loads.
2. **Dynamic Engine:** When users filter by specific seasons or teams, the Flask backend performs on-the-fly Pandas operations on the raw dataset to provide accurate, real-time filtered analytics.
