#!/usr/bin/env python3
"""
build_network.py
Red de actores real — extrae co-menciones de fuentes en noticias del mismo día.
Lee: data/processed/news_summary.csv
Genera: data/processed/actors_network.csv (source, target, weight)
"""
import pandas as pd
import os
from itertools import combinations
from datetime import datetime

INPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/processed/news_summary.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/processed/actors_network.csv")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

try:
    df = pd.read_csv(INPUT_FILE)
except Exception as e:
    print(f"Error leyendo {INPUT_FILE}: {e}")
    exit(1)

if "source" not in df.columns or "date" not in df.columns:
    print("news_summary.csv no tiene columnas source/date")
    exit(1)

# Normalizar fecha a día
df["day"] = pd.to_datetime(df["date"], errors="coerce").dt.date

# Por cada día, calcular qué fuentes publicaron juntas (co-actividad)
pairs = {}
for day, group in df.groupby("day"):
    sources = group["source"].unique().tolist()
    if len(sources) < 2:
        continue
    for a, b in combinations(sorted(sources), 2):
        key = (a, b)
        pairs[key] = pairs.get(key, 0) + 1

if not pairs:
    print("No se encontraron co-menciones entre fuentes.")
    exit(0)

records = [{"source": a, "target": b, "weight": w} for (a, b), w in pairs.items()]
result = pd.DataFrame(records).sort_values("weight", ascending=False).head(30)
result["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
result.to_csv(OUTPUT_FILE, index=False)
print(f"CSV de red de actores generado en {OUTPUT_FILE} ({len(result)} relaciones)")
