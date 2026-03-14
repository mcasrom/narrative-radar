#!/usr/bin/env python3
"""
personas_tracking.py
Seguimiento de menciones y sentimiento de personajes políticos clave.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

BASE    = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT   = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT  = os.path.join(BASE, "data/processed/personas_summary.csv")
HISTORY = os.path.join(BASE, "data/processed/personas_history.csv")

# Personajes con alias
PERSONAS = {
    "Sánchez":      ["sánchez","sanchez","pedro sánchez","pedro sanchez"],
    "Feijóo":       ["feijóo","feijoo","alberto feijóo","alberto feijoo","pp "],
    "Abascal":      ["abascal","santiago abascal","vox"],
    "Yolanda Díaz": ["yolanda díaz","yolanda diaz","yolanda","sumar"],
    "Puigdemont":   ["puigdemont","carles puigdemont","junts"],
    "Ayuso":        ["ayuso","isabel díaz ayuso","isabel diaz ayuso"],
    "Illa":         ["illa","salvador illa","psc"],
    "Rajoy":        ["rajoy","mariano rajoy"],
    "Trump":        ["trump","donald trump"],
    "Zelenski":     ["zelenski","zelensky","volodímir","volodimir"],
    "Mazón":        ["mazón","mazon","carlos mazón","carlos mazon"],
    "Puente":       ["puente","óscar puente","oscar puente"],
    "Montero MJ":   ["maría jesús montero","maria jesus montero","montero hacienda"],
    "Irene Montero": ["irene montero","montero podemos","montero igualdad"],
    "Milei":        ["milei","javier milei"],
    "Macron":       ["macron","emmanuel macron"],
    # ── Líderes G20 ──────────────────────────────────────
    "Putin":        ["putin","vladimir putin","vladímir putin"],
    "Xi Jinping":   ["xi jinping","xi","jinping"],
    "Modi":         ["modi","narendra modi"],
    "Scholz":       ["scholz","olaf scholz"],
    "Meloni":       ["meloni","giorgia meloni"],
    "Erdogan":      ["erdogan","erdoğan","recep tayyip"],
    "Lula":         ["lula","lula da silva","luiz inácio"],
    "Starmer":      ["starmer","keir starmer"],
    "Trudeau":      ["trudeau","justin trudeau"],
    "Jamenei":      ["jamenei","khamenei","líder supremo","ayatolá"],
}

POSITIVE_WORDS = {"victoria","acuerdo","apoya","celebra","gana","logra","anuncia",
                  "aprueba","avance","éxito","lidera","propone","defiende","recupera"}
NEGATIVE_WORDS = {"dimite","acusa","denuncia","critica","rechaza","pierde","escándalo",
                  "corrupción","detienen","condena","fracasa","protesta","investigado",
                  "expulsa","suspende","renuncia","derrota","crisis","polémica"}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"[PERSONAS] {now} — Iniciando seguimiento de personajes")

try:
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["title_lower"] = df["title"].fillna("").str.lower()
    print(f"[PERSONAS] {len(df)} noticias analizadas")
except Exception as e:
    print(f"[PERSONAS] ERROR: {e}"); exit(1)

records = []
for persona, aliases in PERSONAS.items():
    pattern = "|".join(aliases)
    mask    = df["title_lower"].str.contains(pattern, regex=True, na=False)
    subset  = df[mask]
    count   = len(subset)
    if count == 0:
        records.append({"persona":persona,"mentions":0,"positive":0,"negative":0,
                        "neutral":0,"sentiment_score":0.0,"top_sources":"","last_title":"","last_update":now})
        continue

    # Sentimiento contextual
    pos = neg = 0
    for title in subset["title_lower"]:
        words = set(title.split())
        p = len(words & POSITIVE_WORDS)
        n = len(words & NEGATIVE_WORDS)
        if p > n:   pos += 1
        elif n > p: neg += 1

    neutral = count - pos - neg
    score   = round((pos - neg) / count, 3)

    top_sources = subset["source"].value_counts().head(5).to_dict()
    last_title  = subset.sort_values("date", ascending=False).iloc[0]["title"] if count > 0 else ""

    records.append({
        "persona":         persona,
        "mentions":        count,
        "positive":        pos,
        "negative":        neg,
        "neutral":         neutral,
        "sentiment_score": score,
        "top_sources":     str(top_sources),
        "last_title":      last_title[:120],
        "last_update":     now
    })

df_result = pd.DataFrame(records).sort_values("mentions", ascending=False)
df_result.to_csv(OUTPUT, index=False)

# Histórico
df_result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_result], ignore_index=True)
    hist = hist.drop_duplicates(subset=["persona","cycle"], keep="last")
else:
    hist = df_result.copy()
hist.to_csv(HISTORY, index=False)

print("\n=== RANKING DE PERSONAJES ===")
for _, row in df_result[df_result["mentions"]>0].iterrows():
    sentiment = "🟢" if row["sentiment_score"] > 0.1 else "🔴" if row["sentiment_score"] < -0.1 else "⚪"
    print(f"  {sentiment} {row['persona']:<15} {row['mentions']:>4} menciones | score: {row['sentiment_score']:+.2f} | +{row['positive']} -{row['negative']}")

print(f"\n[PERSONAS] Completado.")
