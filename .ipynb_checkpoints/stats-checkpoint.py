import pandas as pd
import numpy as np


df = pd.read_csv(r"C:\Users\deole\Desktop\python\ipl\IPL.csv",low_memory=False)
# print(df.columns)
# print(df.head())

numeric_cols = ['runs_batter', 'balls_faced', 'runs_total', 'runs_bowler',
                'team_runs', 'team_balls', 'team_wicket', 'batter_runs',
                'batter_balls', 'bowler_wicket']

df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

print(df.isna().sum())  # show missing‑value count per column
print(df.info())

print(df.info())
print(df.shape)