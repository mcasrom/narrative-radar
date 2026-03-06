#!/usr/bin/env python3
"""
propagation_analysis.py
Índice de propagación real — mide cuántas fuentes distintas cubren el mismo día.
Cuantas más fuentes distintas publican en un día, mayor el índice de propagación.
Lee: data/processed/news_summary.csv
Genera: data/processed/propagation_summary.csv (date, spread_index)
"""
import pandas as pd
import os
from datetime import datetime

INPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/processed/news_summary.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/processed/propagation_summary.csv")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

try:
    df = pd.read_csv(INPUT_FILE)
except Exception as e:
    print(f"Error leyendo {INPUT_FILE}: {e}")
    exit(1)

if "date" not in df.columns or "source" not in df.columns:
    print("news_summary.csv no tiene columnas date/source")
    exit(1)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
df["day"] = df["date"].dt.date

# Spread index = número de fuentes distintas que publican ese día
# normalizado sobre el total de fuentes activas (x10 para escala 0-100)
total_sources = df["source"].nunique()

daily = df.groupby("day").agg(
    news_count=("title", "count"),
    sources_active=("source", "nunique")
).reset_index()

daily["spread_index"] = (daily["sources_active"] / total_sources * 100).round(1)
daily = daily.sort_values("day")
daily["date"] = daily["day"].astype(str)
daily["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")

result = daily[["date", "spread_index", "news_count", "sources_active", "last_update"]]
result.to_csv(OUTPUT_FILE, index=False)
print(f"CSV de propagación generado en {OUTPUT_FILE} ({len(result)} días)")
