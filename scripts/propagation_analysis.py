#!/usr/bin/env python3
import pandas as pd
import os
os.makedirs("../data/processed", exist_ok=True)
CSV_FILE = "../data/processed/propagation_summary.csv"
df = pd.DataFrame({
    'date': pd.date_range(start='2026-03-01', periods=7),
    'spread_index': [10,15,20,18,12,16,14],
    'last_update': pd.Timestamp.now()
})
df.to_csv(CSV_FILE, index=False)
print(f"CSV de propagación generado en {CSV_FILE}")
