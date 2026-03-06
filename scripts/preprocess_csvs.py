#!/usr/bin/env python3
# preprocess_csvs.py
# Script para filtrar y preparar datos reales para el dashboard
# Ajusta CSV para que sean más legibles y con campos útiles para tooltips

import os
import pandas as pd

base_dir = os.path.abspath("../data/processed")

def process_narratives():
    path = os.path.join(base_dir, "narratives_summary.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Agregar columna de ejemplo de titulares para hover si no existe
        if "sample_headlines" not in df.columns:
            df["sample_headlines"] = df["cluster"].apply(lambda x: f"Ejemplo de titular en {x}")
        df.to_csv(path, index=False)
        print(f"Radar Narrativo procesado: {path}")

def process_actors():
    path = os.path.join(base_dir, "actors_network.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Filtrar conexiones menores a peso 1
        df = df[df["weight"] >= 1]
        df.to_csv(path, index=False)
        print(f"Red de Actores procesada: {path}")

def main():
    process_narratives()
    process_actors()
    print("✅ CSVs preparados para el dashboard")

if __name__ == "__main__":
    main()
