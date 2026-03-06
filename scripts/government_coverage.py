#!/usr/bin/env python3
"""
government_coverage.py
Analiza cobertura real de gobierno/oposición por medio usando léxico político.
Lee: data/processed/news_summary.csv
Genera: data/processed/government_coverage.csv (ultimo ciclo)
        data/processed/government_coverage_history.csv (acumulativo)
"""
import pandas as pd
import os
from datetime import datetime

INPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/government_coverage.csv"))
HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/government_coverage_history.csv"))

PRO_GOV     = ["sánchez","psoe","sumar","coalición","progresista","gobierno aprueba","gobierno anuncia","ejecutivo"]
CONTRA_GOV  = ["pp","vox","oposición","feijóo","abascal","moción","censura","escándalo","corrupción","crítica","denuncia"]
NEUTRAL_KW  = ["economía","empleo","ue","europa","internacional","deporte","cultura","ciencia"]

try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)

now = datetime.now().strftime("%Y-%m-%d %H:%M")
records = []

for source, group in df.groupby("source"):
    titles = group["title"].fillna("").str.lower()
    pro   = int(titles.str.contains("|".join(PRO_GOV), regex=True, na=False).sum())
    contra= int(titles.str.contains("|".join(CONTRA_GOV), regex=True, na=False).sum())
    neutral= int(titles.str.contains("|".join(NEUTRAL_KW), regex=True, na=False).sum())
    total = pro + contra + neutral
    if total == 0:
        alignment = "Neutral"
        alignment_score = 0.0
    elif pro > contra:
        alignment = "Pro-Gobierno"
        alignment_score = round(pro / total, 2)
    elif contra > pro:
        alignment = "Contra-Gobierno"
        alignment_score = round(-contra / total, 2)
    else:
        alignment = "Neutral"
        alignment_score = 0.0
    records.append({"source": source, "count": len(group), "alignment": alignment,
                    "alignment_score": alignment_score, "last_update": now})

result = pd.DataFrame(records).sort_values("count", ascending=False)
result.to_csv(OUTPUT, index=False)

# Histórico acumulativo
result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.read_csv(HISTORY)
    hist = pd.concat([hist, result], ignore_index=True)
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)

print(f"CSV de cobertura gobierno generado en {OUTPUT} ({len(result)} fuentes)")
