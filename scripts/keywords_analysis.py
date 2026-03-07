#!/usr/bin/env python3
"""
keywords_analysis.py
Análisis profundo de keywords y frases desde el histórico de tendencias.
Genera: data/processed/keywords_emerging.csv
        data/processed/keywords_decaying.csv
"""
import pandas as pd
import os
from datetime import datetime

HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/trends_history.csv"))
OUT_EMERGING = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/keywords_emerging.csv"))
OUT_DECAYING = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/keywords_decaying.csv"))

try:
    df = pd.read_csv(HISTORY)
except Exception as e:
    print(f"Error leyendo {HISTORY}: {e}"); exit(1)

now = datetime.now().strftime("%Y-%m-%d %H:%M")
cycles = sorted(df["cycle"].unique())

if len(cycles) < 2:
    print("Se necesitan al menos 2 ciclos para calcular emergentes/decayentes")
    exit(0)

last  = df[df["cycle"] == cycles[-1]].set_index("keyword")["count"]
prev  = df[df["cycle"] == cycles[-2]].set_index("keyword")["count"]

# Keywords en ambos ciclos
common = last.index.intersection(prev.index)
delta = (last[common] - prev[common]).reset_index()
delta.columns = ["keyword", "delta"]
delta["count_last"] = last[common].values
delta["count_prev"] = prev[common].values
delta["pct_change"] = ((delta["delta"] / delta["count_prev"]) * 100).round(1)
delta["last_update"] = now

# Emergentes: mayor subida
emerging = delta[delta["delta"] > 0].sort_values("delta", ascending=False).head(15)
emerging.to_csv(OUT_EMERGING, index=False)

# Decayentes: mayor bajada
decaying = delta[delta["delta"] < 0].sort_values("delta").head(15)
decaying.to_csv(OUT_DECAYING, index=False)

print(f"Keywords emergentes: {len(emerging)} | Decayentes: {len(decaying)}")
print(f"Top emergente: {emerging.iloc[0]['keyword']} (+{emerging.iloc[0]['delta']})" if len(emerging) > 0 else "")
print(f"Top decayente: {decaying.iloc[0]['keyword']} ({decaying.iloc[0]['delta']})" if len(decaying) > 0 else "")
