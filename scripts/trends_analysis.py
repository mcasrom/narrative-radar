#!/usr/bin/env python3
"""
trends_analysis.py
Extrae tendencias reales de palabras clave desde titulares usando TF-IDF.
Lee: data/processed/news_summary.csv
Genera: data/processed/trends_summary.csv (ultimo ciclo)
        data/processed/trends_history.csv (acumulativo)
"""
import pandas as pd
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

INPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/trends_summary.csv"))
HISTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/trends_history.csv"))

STOPWORDS = ["de","la","el","en","y","a","que","los","del","se","las","por","un","con","una","su","al","es","para",
             "como","más","pero","sus","le","ya","o","este","fue","ha","lo","si","sobre","entre","cuando","hasta",
             "sin","no","te","le","da","hay","muy","bien","también","después","antes","donde","desde","según"]

try:
    df = pd.read_csv(INPUT)
except Exception as e:
    print(f"Error leyendo {INPUT}: {e}"); exit(1)

titles = df["title"].fillna("").tolist()
now = datetime.now().strftime("%Y-%m-%d %H:%M")

vectorizer = TfidfVectorizer(stop_words=STOPWORDS, max_features=200, ngram_range=(1,2), min_df=2)
X = vectorizer.fit_transform(titles)
scores = X.sum(axis=0).A1
words = vectorizer.get_feature_names_out()

top_idx = scores.argsort()[::-1][:30]
result = pd.DataFrame([{"keyword": words[i], "count": int(round(scores[i]*100)), "last_update": now} for i in top_idx])
result.to_csv(OUTPUT, index=False)

# Histórico acumulativo
result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.read_csv(HISTORY)
    hist = pd.concat([hist, result], ignore_index=True)
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)

print(f"CSV de tendencias generado en {OUTPUT} ({len(result)} keywords)")
