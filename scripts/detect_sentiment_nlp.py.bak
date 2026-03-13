#!/usr/bin/env python3
"""
detect_sentiment_nlp.py
Análisis de sentimiento NLP para noticias españolas.
Usa léxico expandido específico para medios españoles.
Score por titular: -1.0 (muy negativo) a +1.0 (muy positivo)
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

BASE    = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT   = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT  = os.path.join(BASE, "data/processed/sentiment_summary.csv")
HISTORY = os.path.join(BASE, "data/processed/sentiment_history.csv")

# ── Léxico expandido español para noticias ───────────────────────
POSITIVE = {
    # Logros y victorias
    "victoria","gana","ganan","gano","triunfo","triunfa","logro","logra","éxito",
    "exitoso","exitosa","récord","histórico","histórica","celebra","celebran",
    "acuerdo","aprueba","aprueban","avance","avanza","mejora","mejoran","sube",
    "suben","crece","crecen","crecimiento","aumento","aumenta","supera","superan",
    # Positivo social
    "rescata","rescatan","salva","salvan","ayuda","ayudan","dona","donan",
    "premio","premian","reconoce","reconocen","inauguran","inaugura","abre","abren",
    "lanza","lanzan","descubre","descubren","innova","innovan","revoluciona",
    # Economía positiva
    "beneficios","ganancias","inversión","invierte","invierten","empleo","contrata",
    "contratan","recupera","recuperan","remonta","remontan","máximo","mínimos históricos",
    # Acuerdos y paz
    "paz","pacto","pactan","negocia","negocian","colabora","colaboran","alianza",
    "cooperación","coopera","unidos","unión","integración","libre","libertad",
}

NEGATIVE = {
    # Violencia y conflicto
    "muere","mueren","murió","muerte","fallece","fallecen","falleció","víctima",
    "víctimas","ataque","atacan","ataca","bombardeo","bombardea","bombardean",
    "guerra","conflicto","enfrentamiento","choque","tiroteo","explosión","explota",
    "herido","heridos","detenido","detenidos","arrestado","arrestados",
    # Crisis y desastres
    "crisis","colapsa","colapsan","hunde","hunden","cae","caen","desploma",
    "desploman","pierde","pierden","perdida","tragedia","catástrofe","desastre",
    "incendio","inundación","terremoto","accidente","choque","colisión",
    # Política negativa
    "escándalo","corrupción","fraude","denuncia","denuncian","condena","condenan",
    "dimite","dimiten","expulsa","expulsan","suspende","suspenden","rechaza",
    "rechazan","protesta","protestan","huelga","manifestación","bloquea","bloquean",
    # Economía negativa
    "pérdidas","despide","despiden","cierra","cierran","quiebra","deuda","déficit",
    "recorte","recortan","sube impuestos","inflación","paro","desempleo","pobreza",
    # Amenazas
    "amenaza","amenazan","alerta","peligro","riesgo","emergencia","alarma",
    "advierte","advierten","condena","condenan","acusa","acusan","investigado",
}

INTENSIFIERS = {
    "muy","gran","grave","severo","severa","enorme","masivo","masiva",
    "histórico","histórica","sin precedentes","récord","brutal","dramático",
    "dramática","crítico","crítica","urgente","inmediato","inminente"
}

NEGATORS = {"no","ni","nunca","jamás","sin","falso","falsa","mentira","bulo"}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"[SENTIMENT] {now} — Iniciando análisis de sentimiento NLP")

try:
    df = pd.read_csv(INPUT)
    print(f"[SENTIMENT] {len(df)} noticias cargadas")
except Exception as e:
    print(f"[SENTIMENT] ERROR: {e}"); exit(1)

def analyze_sentiment(title):
    if not title or not isinstance(title, str):
        return 0.0, "neutral"
    
    words = title.lower().split()
    score = 0.0
    negated = False
    intensify = 1.0

    for i, word in enumerate(words):
        # Detectar negadores
        if word in NEGATORS:
            negated = True
            continue
        # Detectar intensificadores
        if word in INTENSIFIERS:
            intensify = 1.5
            continue
        # Puntuar
        if word in POSITIVE:
            score += (1.0 * intensify) * (-1 if negated else 1)
            negated = False; intensify = 1.0
        elif word in NEGATIVE:
            score += (-1.0 * intensify) * (-1 if negated else 1)
            negated = False; intensify = 1.0

    # Normalizar por longitud
    if len(words) > 0:
        score = score / (1 + np.log1p(len(words)))

    # Clasificar
    if score > 0.15:
        label = "positivo"
    elif score < -0.15:
        label = "negativo"
    else:
        label = "neutral"

    return round(score, 3), label

# Analizar todos los titulares
import time
start = time.time()
results = df["title"].fillna("").apply(lambda t: pd.Series(analyze_sentiment(t), index=["score","sentiment"]))
df["score"]     = results["score"]
df["sentiment"] = results["sentiment"]
elapsed = time.time() - start
print(f"[SENTIMENT] {len(df)} titulares analizados en {elapsed:.2f}s")

# ── Resumen global ────────────────────────────────────────────────
summary_global = df["sentiment"].value_counts().reset_index()
summary_global.columns = ["sentiment", "count"]
summary_global["pct"] = (summary_global["count"] / len(df) * 100).round(1)
summary_global["avg_score"] = summary_global["sentiment"].map(
    df.groupby("sentiment")["score"].mean().round(3))
summary_global["last_update"] = now
summary_global.to_csv(OUTPUT, index=False)

# ── Resumen por fuente ────────────────────────────────────────────
by_source = df.groupby("source").agg(
    avg_score=("score","mean"),
    positive=("sentiment", lambda x: (x=="positivo").sum()),
    negative=("sentiment", lambda x: (x=="negativo").sum()),
    neutral=("sentiment",  lambda x: (x=="neutral").sum()),
    total=("sentiment","count")
).reset_index()
by_source["positivity_pct"] = (by_source["positive"] / by_source["total"] * 100).round(1)
by_source["negativity_pct"] = (by_source["negative"] / by_source["total"] * 100).round(1)
by_source["avg_score"]      = by_source["avg_score"].round(3)
by_source["last_update"]    = now
by_source_path = os.path.join(os.path.dirname(OUTPUT), "sentiment_by_source.csv")
by_source.to_csv(by_source_path, index=False)

# ── Histórico ─────────────────────────────────────────────────────
summary_global["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), summary_global], ignore_index=True)
    hist = hist.drop_duplicates(subset=["sentiment","cycle"], keep="last")
else:
    hist = summary_global.copy()
hist.to_csv(HISTORY, index=False)

# ── Resultado ─────────────────────────────────────────────────────
print(f"\n=== DISTRIBUCIÓN DE SENTIMIENTO ===")
for _, row in summary_global.iterrows():
    bar = "█" * int(row["pct"] / 3)
    print(f"  {row['sentiment']:<10} {row['count']:>5} ({row['pct']:>5.1f}%) {bar}")

print(f"\n=== TOP 5 FUENTES MÁS NEGATIVAS ===")
for _, row in by_source.sort_values("negativity_pct", ascending=False).head(5).iterrows():
    print(f"  {row['negativity_pct']:>5.1f}% negativo | {row['source']}")

print(f"\n=== TOP 5 FUENTES MÁS POSITIVAS ===")
for _, row in by_source.sort_values("positivity_pct", ascending=False).head(5).iterrows():
    print(f"  {row['positivity_pct']:>5.1f}% positivo | {row['source']}")

print(f"\n[SENTIMENT] Completado.")
