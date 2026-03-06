#!/usr/bin/env python3
"""
mass_media_analysis.py
Intensidad de cobertura real por medio. Con histórico acumulativo.
"""
import pandas as pd
import os
from datetime import datetime

INPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/mass_media_coverage.csv"))
HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/mass_media_history.csv"))
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)

now = datetime.now().strftime("%Y-%m-%d %H:%M")
counts = df["source"].value_counts().reset_index()
counts.columns = ["source","news_count"]
counts["intensity_index"] = (counts["news_count"] / counts["news_count"].max() * 100).round(1)
counts["last_update"] = now
counts.to_csv(OUTPUT, index=False)

counts["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), counts], ignore_index=True)
    hist = hist.drop_duplicates(subset=["source","cycle"], keep="last")
else:
    hist = counts.copy()
hist.to_csv(HISTORY, index=False)
print(f"CSV de Análisis Masivos generado en {OUTPUT} ({len(counts)} fuentes)")
