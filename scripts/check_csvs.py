#!/usr/bin/env python3
# check_csvs.py
# Script para inspeccionar los CSV generados por el pipeline
# Permite ver primeras filas y columnas de cada CSV

import os
import pandas as pd

base_dir = os.path.abspath("../data/processed")
files = [
    "narratives_summary.csv",
    "emotions_summary.csv",
    "polarization_summary.csv",
    "actors_network.csv",
    "propagation_summary.csv",
    "trends_summary.csv",
    "government_coverage.csv",
    "mass_media_coverage.csv"
]

print("=== Inspección rápida de CSV generados ===")

for f in files:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            print(f"\n=== {f} ===")
            print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")
            print(df.head(5))
        except Exception as e:
            print(f"Error leyendo {f}: {e}")
    else:
        print(f"{f} no existe en {base_dir}")
