#!/usr/bin/env python3
import pandas as pd
import os
os.makedirs("../data/processed", exist_ok=True)
CSV_FILE = "../data/processed/trends_summary.csv"
df = pd.DataFrame({
    'keyword': ['elecciones','gobierno','economía','educación','sanidad'],
    'count':[50,40,30,20,10],
    'last_update': pd.Timestamp.now()
})
df.to_csv(CSV_FILE, index=False)
print(f"CSV de tendencias generado en {CSV_FILE}")
