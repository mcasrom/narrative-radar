#!/usr/bin/env python3
"""Purga ficheros históricos — mantiene N días de datos"""
import pandas as pd
from datetime import datetime, timedelta
import os

BASE = "data/processed"
HOY = datetime.now()

def purgar(fichero, col_fecha, dias=30):
    path = f"{BASE}/{fichero}"
    if not os.path.exists(path):
        return
    df = pd.read_csv(path)
    antes = len(df)
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce', utc=True)
    df = df[df[col_fecha] >= pd.Timestamp(HOY, tz="UTC") - pd.Timedelta(days=dias)]
    df.to_csv(path, index=False)
    print(f"[PURGE] {fichero}: {antes} → {len(df)} filas ({dias}d)")

# news_summary — 7 días
purgar("news_summary.csv", "date", dias=7)

# históricos — 30 días
for item in [
    ("hate_history.csv",               "detected_at", 7),
    ("polarization_history.csv", "date"),
    ("government_coverage_history.csv","last_update"),
    ("agenda_history.csv", "last_update"),
    ("diversity_history.csv", "last_update"),
    ("mass_media_history.csv", "last_update"),
    ("actors_network_history.csv", "last_update"),
    ("personas_history.csv", "last_update"),
    ("trends_history.csv", "last_update"),
    ("emotions_history.csv", "last_update"),
    ("ideology_history.csv", "last_update"),
    ("coordination_history.csv", "detected_at"),
    ("narratives_history.csv", "last_update"),
    ("audit_quality_history.csv", "timestamp"),
]:
    purgar(item[0], item[1], item[2] if len(item)>2 else 30)

print("[PURGE] Completado.")
