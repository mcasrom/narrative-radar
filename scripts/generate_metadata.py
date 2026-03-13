#!/usr/bin/env python3
"""generate_metadata.py — genera metadata.json con fecha real de ingestión"""
import json, os, pandas as pd
from datetime import datetime

BASE   = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUTPUT = os.path.join(BASE, "data/processed/metadata.json")

df = pd.read_csv(os.path.join(BASE, "data/processed/news_summary.csv"))
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df[df["date"] < pd.Timestamp("2026-04-01")]  # filtrar fechas espurias

meta = {
    "last_ingestion": df["date"].max().strftime("%Y-%m-%d %H:%M:%S"),
    "total_news": len(df),
    "sources": int(df["source"].nunique()),
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
with open(OUTPUT, "w") as f:
    json.dump(meta, f, indent=2)
print(f"[META] {meta}")
