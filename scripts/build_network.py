#!/usr/bin/env python3
"""
build_network.py
Red de actores real — co-menciones de fuentes en noticias del mismo día.
Con histórico acumulativo.
"""
import pandas as pd
import os
from itertools import combinations
from datetime import datetime

INPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/actors_network.csv"))
HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/actors_network_history.csv"))
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)

df["day"] = pd.to_datetime(df["date"], errors="coerce").dt.date
now = datetime.now().strftime("%Y-%m-%d %H:%M")

pairs = {}
for day, group in df.groupby("day"):
    sources = group["source"].unique().tolist()
    if len(sources) < 2:
        continue
    for a, b in combinations(sorted(sources), 2):
        pairs[(a, b)] = pairs.get((a, b), 0) + 1

if not pairs:
    print("No se encontraron co-menciones."); exit(0)

result = pd.DataFrame([{"source": a, "target": b, "weight": w} for (a,b),w in pairs.items()])
result = result.sort_values("weight", ascending=False).head(30)
result["last_update"] = now
result.to_csv(OUTPUT, index=False)

result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), result], ignore_index=True)
    hist = hist.drop_duplicates(subset=["source","target","cycle"], keep="last")
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)
print(f"CSV de red de actores generado en {OUTPUT} ({len(result)} relaciones)")
