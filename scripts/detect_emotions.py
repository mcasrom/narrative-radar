#!/usr/bin/env python3
"""
detect_emotions.py
Detecta emociones reales en titulares usando vocabulario léxico por categoría.
Lee: data/processed/news_summary.csv
Genera: data/processed/emotions_summary.csv (ultimo ciclo)
        data/processed/emotions_history.csv (acumulativo)
"""
import pandas as pd
import os
from datetime import datetime

INPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/emotions_summary.csv"))
HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/emotions_history.csv"))

LEXICON = {
    "Alegría":   ["celebra","gana","victoria","acuerdo","éxito","logro","récord","avance","mejora","crecimiento"],
    "Tristeza":  ["muerte","fallece","tragedia","víctima","pérdida","luto","dolor","crisis","colapso","desastre"],
    "Miedo":     ["amenaza","peligro","riesgo","alerta","ataque","terror","miedo","emergencia","explosión","alarma"],
    "Ira":       ["protesta","huelga","enfrentamiento","condena","escándalo","corrupción","fraude","rechazo","denuncia","indignación"],
    "Sorpresa":  ["inesperado","sorpresa","giro","cambio","repentino","imprevisto","histórico","inédito","récord","nuevo"],
    "Neutral":   []
}

try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)

titles = df["title"].fillna("").str.lower()
now = datetime.now().strftime("%Y-%m-%d %H:%M")

counts = {}
for emotion, keywords in LEXICON.items():
    if not keywords:
        continue
    mask = titles.str.contains("|".join(keywords), regex=True, na=False)
    counts[emotion] = int(mask.sum())

# Neutral = titulares sin ninguna emoción detectada
detected = sum(counts.values())
counts["Neutral"] = max(0, len(df) - detected)

result = pd.DataFrame([{"emotion": k, "count": v, "last_update": now} for k, v in counts.items()])
result = result.sort_values("count", ascending=False)
result.to_csv(OUTPUT, index=False)

# Histórico acumulativo
result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.read_csv(HISTORY)
    hist = pd.concat([hist, result], ignore_index=True)
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)

print(f"CSV de emociones generado en {OUTPUT} ({len(result)} emociones, {detected} titulares con emoción detectada)")
