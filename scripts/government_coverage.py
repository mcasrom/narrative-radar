#!/usr/bin/env python3
import pandas as pd
import os
os.makedirs("../data/processed", exist_ok=True)
CSV_FILE = "../data/processed/government_coverage.csv"
df = pd.DataFrame({
    'source':['Medio A','Medio B','Medio C'],
    'count':[20,15,10],
    'alignment':['Pro-Gobierno','Contra-Gobierno','Neutral'],
    'last_update': pd.Timestamp.now()
})
df.to_csv(CSV_FILE, index=False)
print(f"CSV de cobertura gobierno generado en {CSV_FILE}")
