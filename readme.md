# IPL 2008–2025 Data Analysis

Jupyter notebook for analyzing IPL ball‑by‑ball data (2008–2025), including:
- Top run‑scorers
- Most sixes and fours
- Most wickets
- Team‑wise stats

---

## 1. Prerequisites

You need:
- Python 3.8+
- `pandas`, `numpy`, `jupyter`

Install dependencies:

```bash
pip install pandas numpy jupyter
```

---

## 2. Dataset Setup

1. Download the IPL dataset from Kaggle:
   - https://www.kaggle.com/datasets/chaitu20/ipl-dataset2008-2025
   
2. Unzip and place the CSV file (e.g., `IPL.csv`) in your project folder:

 ipl-data-analysis/
├── ipl_stats.ipynb
├── data/
│ └── IPL.csv <-- your Kaggle CSV
└── README.md

3. Update the file path in the notebook (if needed):

```python
df = pd.read_csv("data/IPL.csv", low_memory=False)
```

---

## 3. Run Jupyter Notebook

In your project folder:

```bash
jupyter notebook
```

or

```bash
jupyter lab
```

- Open `ipl_stats.ipynb`.
- Run all cells (Kernel → Restart & Run All) to see:
- data cleaning steps
- derived stats (top runs, sixes, wickets, etc.)

---

## 4. What You Can Extend

You can:
- Add filters (e.g., specific seasons, teams, or formats).
- Add plots (using `matplotlib` or `seaborn`).
- Export clean stats to smaller CSV files (under 100 MB) for sharing.