#!/usr/bin/env python3
"""
detect_polarization.py
Calcula índice de polarización real midiendo diversidad ideológica de fuentes por día.
Fuentes clasificadas: progresistas vs conservadoras. Índice = divergencia entre bloques.
Lee: data/processed/news_summary.csv
Genera: data/processed/polarization_summary.csv (ultimo ciclo)
        data/processed/polarization_history.csv (acumulativo)
"""
import pandas as pd
import os
from datetime import datetime

INPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/polarization_summary.csv"))
HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/polarization_history.csv"))

PROGRESSIVE = {"elpais","eldiario","publico","infolibre","newtral","maldita","bbc_mundo","france24_es","elpais_internacional"}
CONSERVATIVE = {"elmundo","abc","okdiario","vozpopuli","expansion","cope","elespanol","elmundo_espana","elmundo_internacional"}

try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
df["day"] = df["date"].dt.date

now = datetime.now().strftime("%Y-%m-%d %H:%M")
records = []

for day, group in df.groupby("day"):
    prog = group["source"].isin(PROGRESSIVE).sum()
    cons = group["source"].isin(CONSERVATIVE).sum()
    total = prog + cons
    if total == 0:
        continue
    # Índice de polarización: cuanto más desequilibrado, más alto (0=equilibrio, 1=un solo bloque)
    index = round(abs(prog - cons) / total, 3)
    records.append({"date": str(day), "polarization_index": index,
                    "progressive_count": int(prog), "conservative_count": int(cons),
                    "last_update": now})

result = pd.DataFrame(records).sort_values("date")
result.to_csv(OUTPUT, index=False)

# Histórico acumulativo
result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.read_csv(HISTORY)
    hist = pd.concat([hist, result], ignore_index=True)
    hist = hist[(pd.to_datetime(hist["date"], errors="coerce") >= (pd.Timestamp.now() - pd.Timedelta(days=90))) & (pd.to_datetime(hist["date"], errors="coerce") <= pd.Timestamp.now())]
    hist = hist.drop_duplicates(subset=["date","cycle"], keep="last")
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)

print(f"CSV de polarización generado en {OUTPUT} ({len(result)} días)")
