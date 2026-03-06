#!/usr/bin/env python3
import pandas as pd
import os
os.makedirs("../data/processed", exist_ok=True)
CSV_FILE = "../data/processed/actors_network.csv"
df = pd.DataFrame({
    'source': ['Media A','Media B','Politico X','Politico Y'],
    'target': ['Politico X','Politico Y','Media B','Media A'],
    'weight':[5,3,4,2],
    'last_update': pd.Timestamp.now()
})
df.to_csv(CSV_FILE, index=False)
print(f"CSV de red de actores generado en {CSV_FILE}")
