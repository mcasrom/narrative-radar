#!/usr/bin/env python3
# generate_sample_data.py
# Generador de datos de ejemplo para Centro de Mando Narrativo España 🇪🇸

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
os.makedirs(base_dir, exist_ok=True)

# -----------------------------
# Radar Narrativo
# -----------------------------
clusters = ['Economía', 'Política', 'Salud', 'Educación', 'Medioambiente']
n_news = [50, 80, 40, 30, 20]
df_narratives = pd.DataFrame({'cluster': clusters, 'count': n_news})
df_narratives.to_csv(os.path.join(base_dir, "narratives_summary.csv"), index=False)

# -----------------------------
# Radar Emocional
# -----------------------------
emotions = ['Positivo', 'Negativo', 'Neutral']
emotion_counts = [120, 75, 60]
df_emotions = pd.DataFrame({'emotion': emotions, 'count': emotion_counts})
df_emotions.to_csv(os.path.join(base_dir, "emotions_summary.csv"), index=False)

# -----------------------------
# Polarización
# -----------------------------
dates = [datetime.today() - timedelta(days=i) for i in range(10)]
polarization_index = np.round(np.random.uniform(0, 1, size=10), 2)
df_polarization = pd.DataFrame({'date': [d.strftime("%Y-%m-%d") for d in dates],
                                'polarization_index': polarization_index})
df_polarization.to_csv(os.path.join(base_dir, "polarization_summary.csv"), index=False)

# -----------------------------
# Red de Actores
# -----------------------------
sources = ['El País', 'ABC', 'La Vanguardia', 'RTVE', 'El Mundo']
targets = ['Twitter', 'Facebook', 'Instagram', 'TikTok', 'YouTube']
df_actors = pd.DataFrame({
    'source': np.random.choice(sources, 15),
    'target': np.random.choice(targets, 15),
    'weight': np.random.randint(1, 20, 15),
    'last_update': [datetime.today().strftime("%Y-%m-%d %H:%M:%S")]*15
})
df_actors.to_csv(os.path.join(base_dir, "actors_network.csv"), index=False)

# -----------------------------
# Propagación
# -----------------------------
spread_index = np.round(np.random.uniform(0, 100, size=10), 2)
df_propagation = pd.DataFrame({'date': [d.strftime("%Y-%m-%d") for d in dates],
                               'spread_index': spread_index})
df_propagation.to_csv(os.path.join(base_dir, "propagation_summary.csv"), index=False)

# -----------------------------
# Tendencias
# -----------------------------
keywords = ['Inflación', 'Reforma', 'Vacuna', 'Clima', 'Educación']
counts = np.random.randint(5, 50, size=5)
df_trends = pd.DataFrame({'keyword': keywords, 'count': counts})
df_trends.to_csv(os.path.join(base_dir, "trends_summary.csv"), index=False)

# -----------------------------
# Cobertura Gobierno
# -----------------------------
alignment = np.random.choice(['Positivo', 'Negativo', 'Neutral'], size=5)
df_gov = pd.DataFrame({'source': sources[:5], 'alignment': alignment})
df_gov.to_csv(os.path.join(base_dir, "government_coverage.csv"), index=False)

# -----------------------------
# Análisis Masivos
# -----------------------------
intensity_index = np.round(np.random.uniform(10, 100, size=10), 2)
df_massive = pd.DataFrame({
    'last_update': [d.strftime("%Y-%m-%d") for d in dates],
    'intensity_index': intensity_index,
    'source': np.random.choice(sources, 10)
})
df_massive.to_csv(os.path.join(base_dir, "mass_media_coverage.csv"), index=False)

print(f"✅ Datos de ejemplo generados en: {base_dir}")
