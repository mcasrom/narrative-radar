#!/usr/bin/env python3
"""
detect_coordination.py
Detecta narrativas coordinadas — grupos de medios que publican titulares
semánticamente similares en una ventana temporal corta (2 horas).
"""
import pandas as pd
import numpy as np
import os
import yaml
import smtplib
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from email.mime.text import MIMEText
from itertools import combinations

BASE      = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT     = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT    = os.path.join(BASE, "data/processed/coordination_alerts.csv")
HISTORY   = os.path.join(BASE, "data/processed/coordination_history.csv")
EMAIL_CFG = os.path.join(BASE, "config/email.yaml")

SIMILARITY_THRESHOLD = 0.45  # similitud mínima entre titulares
MIN_SOURCES          = 3     # mínimo de fuentes distintas coordinadas
WINDOW_HOURS         = 2     # ventana temporal en horas
RECENT_DAYS          = 3     # solo analizar noticias de los últimos N días

STOPWORDS = ["de","la","el","en","y","a","que","los","del","se","las","por",
             "un","con","una","su","al","es","para","como","mas","pero","no",
             "este","fue","ha","lo","si","sobre","entre","cuando","hasta",
             "este","esta","estos","estas","ese","esa","esos","esas"]

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
print(f"[COORD] {now_str} — Iniciando detector de narrativas coordinadas")

try:
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    # Filtrar noticias recientes y fechas espurias
    cutoff = now - pd.Timedelta(days=RECENT_DAYS)
    df = df[(df["date"] >= cutoff) & (df["date"] <= now)]
    df = df.drop_duplicates(subset=["title"])
    print(f"[COORD] {len(df)} noticias recientes ({RECENT_DAYS} días)")
except Exception as e:
    print(f"[COORD] ERROR: {e}"); exit(1)

if len(df) < 10:
    print("[COORD] Insuficientes noticias — abortando"); exit(0)

# Agrupar por ventana de 2 horas
df["window"] = df["date"].dt.floor(f"{WINDOW_HOURS}h")
windows = df.groupby("window")

print(f"[COORD] Analizando {len(windows)} ventanas de {WINDOW_HOURS}h...")

alerts = []

for window_time, group in windows:
    if len(group) < MIN_SOURCES:
        continue

    titles  = group["title"].fillna("").tolist()
    sources = group["source"].tolist()

    if len(set(sources)) < MIN_SOURCES:
        continue

    # Vectorizar titulares de esta ventana
    try:
        vec = TfidfVectorizer(stop_words=STOPWORDS, max_features=2000, ngram_range=(1,2))
        X   = vec.fit_transform(titles)
        sim = cosine_similarity(X)
    except Exception:
        continue

    # Buscar clusters coordinados
    n = len(titles)
    visited = set()

    for i in range(n):
        if i in visited:
            continue
        cluster_idx = [i]
        for j in range(i+1, n):
            if j not in visited and sim[i][j] >= SIMILARITY_THRESHOLD:
                cluster_idx.append(j)

        cluster_sources = list(set([sources[k] for k in cluster_idx]))

        if len(cluster_sources) >= MIN_SOURCES:
            cluster_titles = [titles[k] for k in cluster_idx]
            avg_sim = float(np.mean([sim[a][b] for a,b in combinations(cluster_idx,2)])) if len(cluster_idx)>1 else 1.0
            coord_score = min(100, int(avg_sim * len(cluster_sources) * 25))

            # Titular representativo = el más similar al resto
            sim_sums = [sum(sim[k][j] for j in cluster_idx if j!=k) for k in cluster_idx]
            rep_idx  = cluster_idx[int(np.argmax(sim_sums))]

            alerts.append({
                "window":           str(window_time),
                "representative":   titles[rep_idx],
                "sources":          ", ".join(sorted(cluster_sources)),
                "n_sources":        len(cluster_sources),
                "n_titles":         len(cluster_titles),
                "avg_similarity":   round(avg_sim, 3),
                "coord_score":      coord_score,
                "all_titles":       " | ".join(cluster_titles[:5]),
                "detected_at":      now_str
            })
            visited.update(cluster_idx)

df_alerts = pd.DataFrame(alerts) if alerts else pd.DataFrame(
    columns=["window","representative","sources","n_sources","n_titles",
             "avg_similarity","coord_score","all_titles","detected_at"])

if len(df_alerts) > 0:
    df_alerts = df_alerts.sort_values("coord_score", ascending=False)

df_alerts.to_csv(OUTPUT, index=False)
print(f"[COORD] {len(df_alerts)} narrativas coordinadas detectadas")

# Histórico
df_alerts["cycle"] = now_str
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_alerts], ignore_index=True)
    hist = hist.drop_duplicates(subset=["window","representative"], keep="last")
else:
    hist = df_alerts.copy()
hist.to_csv(HISTORY, index=False)
print(f"[COORD] Histórico: {len(hist)} eventos acumulados")

# Email si hay coordinación de alto score
high = df_alerts[df_alerts["coord_score"] >= 50] if len(df_alerts) > 0 else pd.DataFrame()

if len(high) > 0 and os.path.exists(EMAIL_CFG):
    try:
        with open(EMAIL_CFG) as f:
            ecfg = yaml.safe_load(f)
        body  = f"Narrativas coordinadas detectadas — {now_str}\n\n"
        body += f"Total eventos: {len(df_alerts)} | Alto score (>=50): {len(high)}\n\n"
        for _, row in high.head(5).iterrows():
            body += f"[Score: {row['coord_score']}] Ventana: {row['window']}\n"
            body += f"  Fuentes ({row['n_sources']}): {row['sources']}\n"
            body += f"  Titular: {row['representative'][:100]}\n\n"
        body += "-- narrative-radar / Odroid-C2"
        msg = MIMEText(body)
        msg["Subject"] = f"[narrative-radar] 🔴 {len(high)} narrativas coordinadas — {now_str}"
        msg["From"] = ecfg["from"]; msg["To"] = ecfg["to"]
        with smtplib.SMTP(ecfg["smtp_host"], 587) as s:
            s.ehlo(); s.starttls()
            s.login(ecfg["user"], ecfg["password"])
            s.send_message(msg)
        print(f"[COORD] Email enviado ({len(high)} alto score)")
    except Exception as e:
        print(f"[COORD] Email error: {e}")

if len(df_alerts) > 0:
    print("\nTop 5 narrativas coordinadas:")
    for _, row in df_alerts.head(5).iterrows():
        print(f"  [Score:{row['coord_score']}] {row['n_sources']} fuentes | {row['window']}")
        print(f"    {row['representative'][:80]}")
        print(f"    Fuentes: {row['sources']}")

print("[COORD] Completado.")
