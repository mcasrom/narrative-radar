#!/usr/bin/env python3
"""
detect_hate.py
Detector de lenguaje agresivo y violento en titulares de noticias españolas.
Genera alertas con score de agresividad.
"""
import pandas as pd
import os
import numpy as np
import yaml
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

BASE    = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT   = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT  = os.path.join(BASE, "data/processed/hate_alerts.csv")
HISTORY = os.path.join(BASE, "data/processed/hate_history.csv")
EMAIL_CFG = os.path.join(BASE, "config/email.yaml")

HATE_THRESHOLD = 2  # mínimo 2 palabras agresivas para alertar

# ── Léxico de lenguaje agresivo/violento en titulares españoles ──
HATE_WORDS = {
    # Violencia física
    "mata","matan","mató","asesina","asesinan","asesinó","golpea","golpean",
    "agrede","agreden","agredió","ataca","atacan","atacó","apuñala","apuñalan",
    "dispara","disparan","disparó","explota","explotan","explosión","bombardea",
    "bombardean","destruye","destruyen","quema","queman","incendia","incendian",
    "amenaza","amenazan","secuestra","secuestran","tortura","torturan",
    # Violencia verbal e insultos en titulares
    "insulta","insultan","insulto","ataca verbalmente","acosa","acosan",
    "humilla","humillan","degrada","degradan","menosprecia","menosprecian",
    "tacha de","llama fascista","llama terrorista","llama corrupto",
    # Lenguaje de confrontación extrema
    "guerra total","batalla campal","enfrentamiento violento","choque violento",
    "pelea","peleas","bronca","broncas","trifulca","altercado","disturbio",
    "disturbios","vandalismo","saqueo","saqueos","linchamiento",
    # Lenguaje discriminatorio
    "invasión","invasores","horda","hordas","banda criminal","mafia",
    "delincuentes","criminales","terroristas","extremistas","radicales",
    # Amenazas institucionales
    "golpe de estado","golpista","golpistas","derrocar","derrocamiento",
    "asalto","asaltan","toma por la fuerza","rendición","capitulación",
    # Catastrofismo agresivo
    "caos total","colapso total","destrucción","aniquilar","aniquilan",
    "eliminar","exterminir","arrasar","arrasarán","acabar con",
}

INTENSIFIERS = {
    "brutal","violento","violenta","salvaje","extremo","extrema",
    "masivo","masiva","grave","severo","severa","sin precedentes",
}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"[HATE] {now} — Iniciando detector de lenguaje agresivo")

try:
    df = pd.read_csv(INPUT)
    print(f"[HATE] {len(df)} noticias cargadas")
except Exception as e:
    print(f"[HATE] ERROR: {e}"); exit(1)

# Contexto bélico — no genera alerta de odio
WAR_CONTEXT = {"irán","iran","israel","ucrania","ukraine","rusia","russia",
               "gaza","líbano","libano","siria","syria","palestina","hamas","hezbollah",
               "pakistán","pakistan","afganistán","afganistan","kabul","ormuz","jark",
               "irak","iraq","yemen","sudán","sudan","libia","somalia","myanmar"}

def analyze_hate(title):
    if not title or not isinstance(title, str):
        return 0, [], False
    # Excluir titulares de conflictos bélicos conocidos
    words_lower = set(title.lower().split())
    if words_lower & WAR_CONTEXT:
        return 0, [], False
    words = title.lower().split()
    hits = []
    intensified = False
    score = 0
    for word in words:
        if word in INTENSIFIERS:
            intensified = True
        if word in HATE_WORDS:
            hits.append(word)
            score += 1.5 if intensified else 1.0
            intensified = False
    return round(score, 2), hits, len(hits) > 0

# Analizar titulares
alerts = []
for _, row in df.iterrows():
    title = str(row.get("title", ""))
    score, hits, is_hate = analyze_hate(title)
    if is_hate and score >= HATE_THRESHOLD:
        alerts.append({
            "source":     row.get("source", ""),
            "title":      title,
            "date":       row.get("date", ""),
            "link":       row.get("link", ""),
            "hate_words": ", ".join(hits),
            "hate_score": score,
            "detected_at": now,
        })

df_alerts = pd.DataFrame(alerts) if alerts else pd.DataFrame(
    columns=["source","title","date","link","hate_words","hate_score","detected_at"])

if len(df_alerts) > 0:
    df_alerts = df_alerts.sort_values("hate_score", ascending=False)

df_alerts.to_csv(OUTPUT, index=False)
print(f"[HATE] {len(df_alerts)} alertas generadas")

# ── Resumen por fuente ────────────────────────────────────────────
if len(df_alerts) > 0:
    by_source = df_alerts.groupby("source").agg(
        total_alerts=("hate_score","count"),
        avg_score=("hate_score","mean"),
        max_score=("hate_score","max"),
    ).reset_index().sort_values("total_alerts", ascending=False)
    print(f"\n=== TOP 5 FUENTES MÁS AGRESIVAS ===")
    for _, row in by_source.head(5).iterrows():
        print(f"  {row['total_alerts']:>3} alertas | avg:{row['avg_score']:.1f} | {row['source']}")

# ── Histórico ─────────────────────────────────────────────────────
df_alerts["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_alerts], ignore_index=True)
    hist = hist.drop_duplicates(subset=["title","cycle"], keep="last")
else:
    hist = df_alerts.copy()
hist.to_csv(HISTORY, index=False)
print(f"[HATE] Histórico: {len(hist)} alertas acumuladas")

# ── Email si hay alertas de alto score ───────────────────────────
high = df_alerts[df_alerts["hate_score"] >= 3] if len(df_alerts) > 0 else pd.DataFrame()
if len(high) > 0 and os.path.exists(EMAIL_CFG):
    try:
        with open(EMAIL_CFG) as f:
            cfg = yaml.safe_load(f)
        body = f"[HATE] {len(high)} titulares con lenguaje muy agresivo:\n\n"
        for _, row in high.head(5).iterrows():
            body += f"[{row['hate_score']}] {row['source']}: {row['title'][:80]}\n"
            body += f"  Palabras: {row['hate_words']}\n\n"
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = f"⚠️ Lenguaje agresivo detectado — {len(high)} alertas"
        msg["From"]    = cfg["user"]
        msg["To"]      = cfg["to"]
        with smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"]) as s:
            s.login(cfg["user"], cfg["password"])
            s.sendmail(cfg["user"], cfg["to"], msg.as_string())
        print(f"[HATE] Email enviado ({len(high)} alertas alto score)")
    except Exception as e:
        print(f"[HATE] Email error: {e}")

print(f"[HATE] Completado.")
