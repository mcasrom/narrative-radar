#!/usr/bin/env python3
import pandas as pd
import os
os.makedirs("../data/processed", exist_ok=True)
CSV_FILE = "../data/processed/emotions_summary.csv"
df = pd.DataFrame({
    'emotion': ['Alegría', 'Tristeza', 'Miedo', 'Ira', 'Sorpresa'],
    'count': [10, 5, 8, 3, 7],
    'last_update': pd.Timestamp.now()
})
df.to_csv(CSV_FILE, index=False)
print(f"CSV de emociones generado en {CSV_FILE}")
