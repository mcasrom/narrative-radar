#!/usr/bin/env python3
# generate_sample_data.py
# Genera CSV de ejemplo con datos realistas para arrancar dashboard

import os
import pandas as pd
from datetime import datetime, timedelta
import random

base_dir = os.path.abspath("data/processed")
os.makedirs(base_dir, exist_ok=True)

# -----------------------------
# Radar Narrativo
# -----------------------------
clusters = ["Economía", "Política", "Sanidad", "Educación", "Internacional"]
data = []
for c in clusters:
    data.append({"cluster": c, "count": random.randint(10, 100)})
pd.DataFrame(data).to_csv(os.path.join(base_dir, "narratives_summary.csv"), index=False)

# -----------------------------
# Radar Emocional
# -----------------------------
emotions = ["Positiva", "Negativa", "Neutral"]
data = []
for e in emotions:
    data.append({"emotion": e, "count": random.randint(50, 200)})
pd.DataFrame(data).to_csv(os.path.join(base_dir, "emotions_summary.csv"), index=False)

# -----------------------------
# Polarización
# -----------------------------
dates = [datetime.today() - timedelta(days=i) for i in range(10)]
data = [{"date": d.strftime("%Y-%m-%d"), "polarization_index": random.uniform(0,1)} for d in dates]
pd.DataFrame(data).to_csv(os.path.join(base_dir, "polarization_summary.csv"), index=False)

# -----------------------------
# Red de Actores
# -----------------------------
actors = ["MedioA", "MedioB", "MedioC", "MedioD"]
data = []
for s in actors:
    for t in actors:
        if s != t:
            data.append({"source": s, "target": t, "weight": random.randint(1,5), "last_update": datetime.today().strftime("%Y-%m-%d")})
pd.DataFrame(data).to_csv(os.path.join(base_dir, "actors_network.csv"), index=False)

# -----------------------------
# Propagación
# -----------------------------
data = [{"date": d.strftime("%Y-%m-%d"), "spread_index": random.uniform(0,1)} for d in dates]
pd.DataFrame(data).to_csv(os.path.join(base_dir, "propagation_summary.csv"), index=False)

# -----------------------------
# Tendencias
# -----------------------------
keywords = ["inflación", "gobierno", "vacuna", "educación", "conflicto"]
data = [{"keyword": k, "count": random.randint(10,50)} for k in keywords]
pd.DataFrame(data).to_csv(os.path.join(base_dir, "trends_summary.csv"), index=False)

# -----------------------------
# Cobertura Gobierno
# -----------------------------
sources = ["MedioA", "MedioB", "MedioC"]
alignments = ["Positiva", "Negativa", "Neutral"]
data = []
for s in sources:
    data.append({"source": s, "alignment": random.choice(alignments)})
pd.DataFrame(data).to_csv(os.path.join(base_dir, "government_coverage.csv"), index=False)

# -----------------------------
# Análisis Masivos
# -----------------------------
data = []
for s in sources:
    for d in dates:
        data.append({"source": s, "last_update": d.strftime("%Y-%m-%d"), "intensity_index": random.randint(10,100)})
pd.DataFrame(data).to_csv(os.path.join(base_dir, "mass_media_coverage.csv"), index=False)

print(f"✅ CSV de ejemplo generados en {base_dir}")
