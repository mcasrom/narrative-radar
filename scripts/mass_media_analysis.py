#!/usr/bin/env python3
"""
mass_media_analysis.py
Intensidad de cobertura real por medio — cuenta noticias por fuente
y calcula un índice de intensidad normalizado (0-100).
Lee: data/processed/news_summary.csv
Genera: data/processed/mass_media_coverage.csv (source, intensity_index)
"""
import pandas as pd
import os
from datetime import datetime

INPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/processed/news_summary.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/processed/mass_media_coverage.csv")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

try:
    df = pd.read_csv(INPUT_FILE)
except Exception as e:
    print(f"Error leyendo {INPUT_FILE}: {e}")
    exit(1)

if "source" not in df.columns:
    print("news_summary.csv no tiene columna source")
    exit(1)

# Contar noticias por fuente
counts = df["source"].value_counts().reset_index()
counts.columns = ["source", "news_count"]

# Normalizar a índice 0-100 sobre el máximo
max_count = counts["news_count"].max()
counts["intensity_index"] = (counts["news_count"] / max_count * 100).round(1)
counts["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")

counts = counts.sort_values("intensity_index", ascending=False)
counts.to_csv(OUTPUT_FILE, index=False)
print(f"CSV de Análisis Masivos generado en {OUTPUT_FILE} ({len(counts)} fuentes)")
