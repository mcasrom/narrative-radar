#!/usr/bin/env python3
"""
agenda_setting.py
Score de agenda-setting — mide qué medios marcan agenda (publican primero)
vs cuáles siguen la agenda ajena.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE     = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT    = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT   = os.path.join(BASE, "data/processed/agenda_score.csv")
HISTORY  = os.path.join(BASE, "data/processed/agenda_history.csv")

SIMILARITY_THRESHOLD = 0.40
WINDOW_HOURS         = 6
RECENT_DAYS          = 3
STOPWORDS = ["de","la","el","en","y","a","que","los","del","se","las","por",
             "un","con","una","su","al","es","para","como","mas","pero","no",
             "este","esta","fue","ha","lo","si","sobre","entre","cuando"]

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
print(f"[AGENDA] {now_str} — Iniciando score de agenda-setting")

try:
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    cutoff = now - pd.Timedelta(days=RECENT_DAYS)
    df = df[(df["date"] >= cutoff) & (df["date"] <= now)]
    df = df.drop_duplicates(subset=["title"])
    df = df.sort_values("date")
    print(f"[AGENDA] {len(df)} noticias recientes ({RECENT_DAYS} días)")
except Exception as e:
    print(f"[AGENDA] ERROR: {e}"); exit(1)

if len(df) < 10:
    print("[AGENDA] Insuficientes noticias"); exit(0)

# Agrupar por ventana de 6h para detectar temas del mismo período
df["window"] = df["date"].dt.floor(f"{WINDOW_HOURS}h")

# Contadores por fuente
source_stats = {s: {"first": 0, "follower": 0, "topics": 0} 
                for s in df["source"].unique()}

topics_found = 0

for window_time, group in df.groupby("window"):
    if len(group) < 2:
        continue

    titles  = group["title"].fillna("").tolist()
    sources = group["source"].tolist()
    dates   = group["date"].tolist()
    indices = list(range(len(titles)))

    try:
        vec = TfidfVectorizer(stop_words=STOPWORDS, max_features=2000, ngram_range=(1,2))
        X   = vec.fit_transform(titles)
        sim = cosine_similarity(X)
    except Exception:
        continue

    visited = set()

    for i in indices:
        if i in visited:
            continue
        # Encontrar cluster de noticias similares
        cluster = [i]
        for j in indices:
            if j != i and j not in visited and sim[i][j] >= SIMILARITY_THRESHOLD:
                cluster.append(j)

        if len(cluster) < 2:
            continue

        # Identificar fuentes únicas en el cluster
        cluster_sources = [sources[k] for k in cluster]
        if len(set(cluster_sources)) < 2:
            visited.update(cluster)
            continue

        # El primero en publicar = agenda-setter
        cluster_dates = [(dates[k], sources[k]) for k in cluster]
        cluster_dates.sort(key=lambda x: x[0])
        first_source = cluster_dates[0][1]
        follower_sources = set(d[1] for d in cluster_dates[1:])

        # Actualizar contadores
        if first_source in source_stats:
            source_stats[first_source]["first"]  += 1
            source_stats[first_source]["topics"] += 1

        for src in follower_sources:
            if src in source_stats:
                source_stats[src]["follower"] += 1
                source_stats[src]["topics"]   += 1

        topics_found += 1
        visited.update(cluster)

print(f"[AGENDA] {topics_found} temas analizados")

# Calcular scores
records = []
for source, stats in source_stats.items():
    total = stats["topics"]
    if total == 0:
        continue
    agenda_score    = round(stats["first"] / total * 100, 1)
    follower_score  = round(stats["follower"] / total * 100, 1)
    news_count      = len(df[df["source"] == source])

    # Clasificación
    if agenda_score >= 40:
        role = "Marcador de agenda"
    elif agenda_score >= 20:
        role = "Mixto"
    elif follower_score >= 60:
        role = "Seguidor"
    else:
        role = "Independiente"

    records.append({
        "source":         source,
        "agenda_score":   agenda_score,
        "follower_score": follower_score,
        "times_first":    stats["first"],
        "times_follower": stats["follower"],
        "topics_total":   total,
        "news_count":     news_count,
        "role":           role,
        "last_update":    now_str
    })

df_result = pd.DataFrame(records).sort_values("agenda_score", ascending=False)
df_result.to_csv(OUTPUT, index=False)
print(f"[AGENDA] Score calculado para {len(df_result)} fuentes")

# Histórico
df_result["cycle"] = now_str
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_result], ignore_index=True)
    hist = hist.drop_duplicates(subset=["source","cycle"], keep="last")
else:
    hist = df_result.copy()
hist.to_csv(HISTORY, index=False)

# Mostrar ranking
print("\n=== RANKING AGENDA-SETTING ===")
for _, row in df_result.head(10).iterrows():
    print(f"  {row['agenda_score']:5.1f}% | {row['role']:<22} | {row['source']}")

print("[AGENDA] Completado.")
