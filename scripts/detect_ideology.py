#!/usr/bin/env python3
"""
detect_ideology.py
Detector de narrativas ideológicas y geopolíticas en titulares españoles.
Detecta posicionamiento respecto a bloques: OTAN, UE, EEUU, Rusia, China, inmigración.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

BASE    = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT   = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT  = os.path.join(BASE, "data/processed/ideology_summary.csv")
HISTORY = os.path.join(BASE, "data/processed/ideology_history.csv")

# ── Léxicos por bloque ideológico ─────────────────────────────────
BLOCKS = {
    "OTAN": {
        "pro":  ["otan","nato","alianza atlántica","aliados","defensa común",
                 "artículo 5","escudo nuclear","ejército europeo","misión otan",
                 "soldados otan","tropas aliadas","expansión otan"],
        "anti": ["anti-otan","anti otan","fuera de la otan","salir de la otan",
                 "no a la otan","contra la otan","imperialismo militar",
                 "bases militares","provocación otan","expansionismo otan",
                 "otan agresor","otan amenaza"],
        "neutral": ["otan","nato","alianza atlántica"],
    },
    "UE": {
        "pro":  ["unión europea","integración europea","euro","eurozona",
                 "fondos europeos","next generation","política europea",
                 "parlamento europeo","comisión europea","von der leyen",
                 "solidaridad europea","mercado único","libre circulación"],
        "anti": ["anti-ue","contra la ue","soberanía nacional","euroskeptic",
                 "euroesceptic","bruselas impone","dictadura europea",
                 "salir de la ue","frexit","italexit","España soberana",
                 "tecnocracia europea","federalismo impuesto"],
        "neutral": ["ue","unión europea","europa","bruselas","comisión europea"],
    },
    "EEUU": {
        "pro":  ["aliado estadounidense","apoyo de washington","respaldo de eeuu",
                 "cooperación con eeuu","trump apoya","biden apoya",
                 "inversión americana","empresas americanas"],
        "anti": ["anti-americano","imperialismo americano","yanqui","yanquis",
                 "intervencionismo","hegemonía americana","cia","trump amenaza",
                 "aranceles trump","eeuu impone","washington ordena",
                 "presión de eeuu","chantaje americano"],
        "neutral": ["eeuu","estados unidos","washington","trump","biden","harris"],
    },
    "Rusia": {
        "pro":  ["putin tiene razón","narrativa rusa","rusia denuncia",
                 "occidente provocó","expansión otan provocó","rusia se defiende",
                 "acuerdo con rusia","gas ruso","energía rusa","diálogo con moscú"],
        "anti": ["agresor ruso","invasión rusa","crímenes de guerra rusos",
                 "putin dictador","régimen de putin","propaganda rusa",
                 "desinformación rusa","sanciones a rusia","rusia ataca",
                 "bombardeos rusos","ocupación rusa","kremlin ordena"],
        "neutral": ["rusia","putin","moscú","kremlin","fuerzas rusas"],
    },
    "China": {
        "pro":  ["cooperación con china","inversión china","acuerdo con pekín",
                 "ruta de la seda","belt and road","tecnología china",
                 "huawei","xi jinping propone","relaciones con china"],
        "anti": ["espionaje chino","amenaza china","china roba","derechos humanos china",
                 "xinjiang","uigures","taiwan china","china invade","represión china",
                 "dictadura china","régimen chino","tiktok espionaje"],
        "neutral": ["china","pekín","beijing","xi jinping","chino","chinos"],
    },
    "Inmigración": {
        "pro":  ["acogida de migrantes","refugiados","derecho de asilo",
                 "integración de inmigrantes","diversidad","multiculturalismo",
                 "regularización","papeles para todos","migrantes trabajan",
                 "aportación de inmigrantes","solidaridad con migrantes"],
        "anti": ["invasión migratoria","efecto llamada","pateras","avalancha migratoria",
                 "control de fronteras","expulsión de migrantes","ilegales",
                 "inmigrantes delincuentes","remesas","ocupación del territorio",
                 "sustitución de población","inmigración ilegal"],
        "neutral": ["inmigrantes","migrantes","refugiados","asilo","fronteras"],
    },
    "MERCOSUR": {
        "pro":  ["acuerdo mercosur","ue mercosur","libre comercio mercosur",
                 "oportunidades mercosur","mercado latinoamericano",
                 "integración latinoamericana","lula","bolsonaro firma"],
        "anti": ["contra mercosur","rechazo mercosur","agricultores contra",
                 "competencia desleal mercosur","dumping mercosur",
                 "productos latinoamericanos","amenaza agrícola"],
        "neutral": ["mercosur","latinoamérica","america latina","brasil","argentina"],
    },
}

def analyze_ideology(title: str) -> dict:
    """Analiza un titular y devuelve scores por bloque."""
    if not title or not isinstance(title, str):
        return {}
    text = title.lower()
    results = {}
    for block, lexicon in BLOCKS.items():
        pro_hits  = sum(1 for w in lexicon["pro"]     if w in text)
        anti_hits = sum(1 for w in lexicon["anti"]    if w in text)
        neu_hits  = sum(1 for w in lexicon["neutral"] if w in text)
        if pro_hits + anti_hits + neu_hits == 0:
            continue  # no menciona este bloque
        if pro_hits + anti_hits == 0:
            stance = "neutral"
            score  = 0.0
        elif pro_hits > anti_hits:
            stance = "pro"
            score  = round(pro_hits / (pro_hits + anti_hits), 2)
        elif anti_hits > pro_hits:
            stance = "anti"
            score  = round(-anti_hits / (pro_hits + anti_hits), 2)
        else:
            stance = "neutral"
            score  = 0.0
        results[block] = {"stance": stance, "score": score,
                          "pro": pro_hits, "anti": anti_hits, "mentions": neu_hits}
    return results

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"[IDEOLOGY] {now} — Iniciando detector de narrativas ideológicas")

try:
    df = pd.read_csv(INPUT)
    print(f"[IDEOLOGY] {len(df)} noticias cargadas")
except Exception as e:
    print(f"[IDEOLOGY] ERROR: {e}"); exit(1)

# Analizar todos los titulares
rows = []
for _, row in df.iterrows():
    result = analyze_ideology(str(row.get("title", "")))
    for block, data in result.items():
        rows.append({
            "block":    block,
            "stance":   data["stance"],
            "score":    data["score"],
            "pro":      data["pro"],
            "anti":     data["anti"],
            "mentions": data["mentions"],
            "source":   row.get("source", ""),
            "title":    str(row.get("title", ""))[:120],
            "date":     row.get("date", ""),
        })

df_results = pd.DataFrame(rows)
print(f"[IDEOLOGY] {len(df_results)} menciones ideológicas detectadas")

if len(df_results) == 0:
    print("[IDEOLOGY] Sin datos — abortando")
    exit(0)

# ── Resumen por bloque ────────────────────────────────────────────
summary = []
for block in BLOCKS.keys():
    df_b = df_results[df_results["block"] == block]
    if len(df_b) == 0:
        continue
    total   = len(df_b)
    pro     = len(df_b[df_b["stance"] == "pro"])
    anti    = len(df_b[df_b["stance"] == "anti"])
    neutral = len(df_b[df_b["stance"] == "neutral"])
    avg_score = df_b["score"].mean()
    dominant = "pro" if pro > anti else ("anti" if anti > pro else "neutral")
    summary.append({
        "block":      block,
        "total":      total,
        "pro":        pro,
        "anti":       anti,
        "neutral":    neutral,
        "avg_score":  round(avg_score, 3),
        "dominant":   dominant,
        "pro_pct":    round(pro / total * 100, 1) if total > 0 else 0,
        "anti_pct":   round(anti / total * 100, 1) if total > 0 else 0,
        "last_update": now,
    })

df_summary = pd.DataFrame(summary).sort_values("total", ascending=False)
df_summary.to_csv(OUTPUT, index=False)
print(f"\n=== NARRATIVAS IDEOLÓGICAS DETECTADAS ===")
for _, row in df_summary.iterrows():
    icon = "🟢" if row["dominant"] == "pro" else ("🔴" if row["dominant"] == "anti" else "⚪")
    print(f"  {icon} {row['block']:<15} {row['total']:>5} menciones | "
          f"pro:{row['pro_pct']:>5.1f}% anti:{row['anti_pct']:>5.1f}% | score:{row['avg_score']:+.3f}")

# ── Histórico ─────────────────────────────────────────────────────
df_summary["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_summary], ignore_index=True)
    hist = hist.drop_duplicates(subset=["block", "cycle"], keep="last")
else:
    hist = df_summary.copy()
hist.to_csv(HISTORY, index=False)
print(f"\n[IDEOLOGY] Histórico: {len(hist)} registros")
print(f"[IDEOLOGY] Completado.")
