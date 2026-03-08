#!/usr/bin/env python3
"""
detect_viral.py
Detecta keywords que explotan >200% en < 2 horas respecto al ciclo anterior.
"""
import pandas as pd
import numpy as np
import os
import yaml
import smtplib
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from email.mime.text import MIMEText

BASE      = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT     = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT    = os.path.join(BASE, "data/processed/viral_topics.csv")
HISTORY   = os.path.join(BASE, "data/processed/viral_history.csv")
EMAIL_CFG = os.path.join(BASE, "config/email.yaml")

VIRAL_THRESHOLD  = 2.0   # 200% de incremento
WINDOW_CURRENT   = 2     # horas ventana actual
WINDOW_BASELINE  = 6     # horas ventana baseline
MIN_COUNT        = 3     # mínimo de apariciones para considerar viral
STOPWORDS = {"de","la","el","en","y","a","que","los","del","se","las","por",
             "un","con","una","su","al","es","para","como","mas","pero","no",
             "este","esta","fue","ha","lo","si","sobre","entre","cuando","hasta",
             "sus","les","más","sin","hay","han","ya","ser","dos","tres","tras",
             "ante","ese","esa","son","era","sido","están","está","será","así","desde","hasta","donde","quien","cuándo","cuando","según","segun","todas","todos","entre","sobre","durante","mismo","misma","parte","hacer","tiene","tienen","cada","solo","unos","unas","dhabi"}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

def email_cooldown_ok(module_name, hours=4):
    """Devuelve True si se puede enviar email (no se ha enviado en las ultimas N horas)"""
    import time
    lock_dir = os.path.join(BASE, "data/processed/.email_locks")
    os.makedirs(lock_dir, exist_ok=True)
    lock_file = os.path.join(lock_dir, f"{module_name}.lock")
    now_ts = time.time()
    if os.path.exists(lock_file):
        last_sent = float(open(lock_file).read().strip())
        if now_ts - last_sent < hours * 3600:
            remaining = int((hours * 3600 - (now_ts - last_sent)) / 60)
            print(f"[{module_name.upper()}] Email en cooldown — faltan {remaining} min")
            return False
    open(lock_file, "w").write(str(now_ts))
    return True

now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
print(f"[VIRAL] {now_str} — Iniciando detector de temas virales")

try:
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df[df["date"] <= now]
    print(f"[VIRAL] {len(df)} noticias cargadas")
except Exception as e:
    print(f"[VIRAL] ERROR: {e}"); exit(1)

def get_word_counts(titles):
    counts = Counter()
    for title in titles:
        if not isinstance(title, str):
            continue
        words = [w.strip(".,;:()[]\"'¿?¡!") for w in title.lower().split()]
        words = [w for w in words if len(w) > 4 and w not in STOPWORDS]
        counts.update(words)
    return counts

# Ventana actual (últimas 2h)
current_start = now - timedelta(hours=WINDOW_CURRENT)
df_current    = df[df["date"] >= current_start]

# Ventana baseline (2h-8h atrás)
baseline_end   = now - timedelta(hours=WINDOW_CURRENT)
baseline_start = now - timedelta(hours=WINDOW_CURRENT + WINDOW_BASELINE)
df_baseline    = df[(df["date"] >= baseline_start) & (df["date"] < baseline_end)]

print(f"[VIRAL] Ventana actual: {len(df_current)} noticias ({WINDOW_CURRENT}h)")
print(f"[VIRAL] Ventana baseline: {len(df_baseline)} noticias ({WINDOW_BASELINE}h)")

counts_current  = get_word_counts(df_current["title"].tolist())
counts_baseline = get_word_counts(df_baseline["title"].tolist())

# Normalizar por tamaño de ventana
n_current  = max(len(df_current), 1)
n_baseline = max(len(df_baseline), 1)

virals = []
for word, count in counts_current.items():
    if count < MIN_COUNT:
        continue
    freq_current  = count / n_current
    baseline_raw  = counts_baseline.get(word, 0)
    freq_baseline = baseline_raw / n_baseline

    if freq_baseline == 0:
        ratio = 5.0 if count >= MIN_COUNT else 0
    else:
        ratio = freq_current / freq_baseline

    if ratio >= VIRAL_THRESHOLD:
        # Titulares representativos
        sample = df_current[df_current["title"].str.lower().str.contains(word, na=False)]
        sources = sample["source"].unique().tolist()[:5]
        titles_sample = sample["title"].head(3).tolist()
        virals.append({
            "keyword":     word,
            "count_now":   count,
            "count_base":  baseline_raw,
            "ratio":       round(ratio, 2),
            "viral_score": min(100, int(ratio * 20)),
            "sources":     ", ".join(sources),
            "n_sources":   len(sources),
            "sample_title": titles_sample[0] if titles_sample else "",
            "detected_at": now_str
        })

df_virals = pd.DataFrame(virals) if virals else pd.DataFrame(
    columns=["keyword","count_now","count_base","ratio","viral_score",
             "sources","n_sources","sample_title","detected_at"])

if len(df_virals) > 0:
    df_virals = df_virals.sort_values("viral_score", ascending=False)

df_virals.to_csv(OUTPUT, index=False)
print(f"[VIRAL] {len(df_virals)} temas virales detectados")

# Histórico
df_virals["cycle"] = now_str
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_virals], ignore_index=True)
    hist = hist.drop_duplicates(subset=["keyword","cycle"], keep="last")
else:
    hist = df_virals.copy()
hist.to_csv(HISTORY, index=False)

# Email si hay virales de alto score
high = df_virals[df_virals["viral_score"] >= 60] if len(df_virals) > 0 else pd.DataFrame()
if len(high) > 0 and os.path.exists(EMAIL_CFG) and email_cooldown_ok("VIRAL", hours=4):
    try:
        with open(EMAIL_CFG) as f:
            ecfg = yaml.safe_load(f)
        body  = f"Temas virales detectados — {now_str}\n\n"
        body += f"Total virales: {len(df_virals)} | Alto score: {len(high)}\n\n"
        for _, row in high.head(5).iterrows():
            body += f"  [{row['viral_score']}] '{row['keyword']}' x{row['ratio']} ({row['count_now']} veces)\n"
            body += f"  Fuentes: {row['sources']}\n"
            body += f"  Ejemplo: {row['sample_title'][:100]}\n\n"
        msg = MIMEText(body)
        msg["Subject"] = f"[narrative-radar] 🔥 {len(high)} temas virales — {now_str}"
        msg["From"] = ecfg["from"]; msg["To"] = ecfg["to"]
        with smtplib.SMTP(ecfg["smtp_host"], 587) as s:
            s.ehlo(); s.starttls()
            s.login(ecfg["user"], ecfg["password"])
            s.send_message(msg)
        print(f"[VIRAL] Email enviado ({len(high)} alto score)")
    except Exception as e:
        print(f"[VIRAL] Email error: {e}")

if len(df_virals) > 0:
    print("\n=== TOP 10 TEMAS VIRALES ===")
    for _, row in df_virals.head(10).iterrows():
        print(f"  [Score:{row['viral_score']:>3}] x{row['ratio']:<5} '{row['keyword']}' ({row['count_now']} veces) — {row['sources'][:60]}")

print("[VIRAL] Completado.")
