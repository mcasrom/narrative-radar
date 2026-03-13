#!/usr/bin/env python3
"""
propagation_analysis.py
Índice de propagación real por día. Con histórico acumulativo.
Mide variación diaria de noticias x diversidad de fuentes.
"""
import pandas as pd
import os
from datetime import datetime
INPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/propagation_summary.csv"))
HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/propagation_history.csv"))
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df[df["date"] < pd.Timestamp("2026-04-01")]
df = df.dropna(subset=["date"])
df["day"] = df["date"].dt.date
now = datetime.now().strftime("%Y-%m-%d %H:%M")
total_sources = df["source"].nunique()
daily = df.groupby("day").agg(
    news_count=("title","count"),
    sources_active=("source","nunique")
).reset_index()
daily = daily.sort_values("day").reset_index(drop=True)
daily["news_pct_change"] = daily["news_count"].pct_change().fillna(0).clip(-1, 2)
daily["spread_index"] = (
    (0.5 + daily["news_pct_change"] * 0.5) *
    (daily["sources_active"] / total_sources) * 100
).clip(0, 100).round(1)
daily["date"] = daily["day"].astype(str)
daily["last_update"] = now
result = daily[["date","spread_index","news_count","sources_active","last_update"]].sort_values("date")
result.to_csv(OUTPUT, index=False)
result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), result], ignore_index=True)
    hist = hist[(pd.to_datetime(hist["date"], errors="coerce") >= (pd.Timestamp.now() - pd.Timedelta(days=90))) & (pd.to_datetime(hist["date"], errors="coerce") <= pd.Timestamp.now())]
    hist = hist.drop_duplicates(subset=["date"], keep="last")
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)
print(f"CSV de propagación generado en {OUTPUT} ({len(result)} días)")
