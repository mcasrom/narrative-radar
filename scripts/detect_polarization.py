#!/usr/bin/env python3
import pandas as pd
import os
os.makedirs("../data/processed", exist_ok=True)
CSV_FILE = "../data/processed/polarization_summary.csv"
df = pd.DataFrame({
    'date': pd.date_range(start='2026-03-01', periods=7),
    'polarization_index': [0.1,0.3,0.5,0.6,0.4,0.2,0.3],
    'last_update': pd.Timestamp.now()
})
df.to_csv(CSV_FILE, index=False)
print(f"CSV de polarización generado en {CSV_FILE}")
