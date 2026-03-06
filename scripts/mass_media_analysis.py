#!/usr/bin/env python3
import pandas as pd
import os
import argparse

# -----------------------------
# Argumentos CLI
# -----------------------------
parser = argparse.ArgumentParser(description="Generar CSV de Análisis Masivos")
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()
seed = args.seed

# -----------------------------
# Carpeta processed
# -----------------------------
processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
os.makedirs(processed_dir, exist_ok=True)
CSV_FILE = os.path.join(processed_dir, "mass_media_coverage.csv")

# -----------------------------
# Datos simulados
# -----------------------------
sources = ["Medio A", "Medio B", "Medio C", "Medio D"]
intensity_index = [seed % 10 + 5, (seed+3) % 10 + 7, (seed+5) % 10 + 6, (seed+7) % 10 + 8]

df = pd.DataFrame({
    "source": sources,
    "intensity_index": intensity_index,
    "last_update": pd.Timestamp.now()
})

df.to_csv(CSV_FILE, index=False)
print(f"CSV de Análisis Masivos generado en {CSV_FILE}")
