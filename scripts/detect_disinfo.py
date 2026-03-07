#!/usr/bin/env python3
import pandas as pd
import feedparser
import socket
import os
import numpy as np
import yaml
import smtplib
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from email.mime.text import MIMEText

socket.setdefaulttimeout(10)

BASE        = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT       = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT      = os.path.join(BASE, "data/processed/disinfo_alerts.csv")
HISTORY     = os.path.join(BASE, "data/processed/disinfo_history.csv")
BULOS_DB    = os.path.join(BASE, "data/processed/disinfo_bulos.csv")
EMAIL_CFG   = os.path.join(BASE, "config/email.yaml")

SIMILARITY_THRESHOLD = 0.40
EXCLUDE_SOURCES = {"maldita", "newtral"}
MALDITA_PATTERNS = ["No, ", "Ni es ", "No es ", "Falso:", "Bulo:"]
NEWTRAL_FAKE_TAGS = ["Fakes", "Bulos", "Fake"]
STOPWORDS = ["de","la","el","en","y","a","que","los","del","se","las","por",
             "un","con","una","su","al","es","para","como","mas","pero","no"]

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"[DISINFO] {now} — Iniciando detector")

try:
    df_news = pd.read_csv(INPUT)
    print(f"[DISINFO] {len(df_news)} noticias cargadas")
except Exception as e:
    print(f"[DISINFO] ERROR: {e}"); exit(1)

bulos = []
try:
    for entry in feedparser.parse("https://maldita.es/feed/").entries:
        title = entry.get("title", "").strip()
        if any(title.startswith(p) for p in MALDITA_PATTERNS):
            claim = title
            for p in MALDITA_PATTERNS:
                if claim.startswith(p):
                    claim = claim[len(p):].strip(); break
            bulos.append({"source":"maldita","title":title,"claim":claim,
                          "link":entry.get("link",""),"date":entry.get("published",now)})
    print(f"[DISINFO] {len(bulos)} bulos maldita")
except Exception as e:
    print(f"[DISINFO] ERROR maldita: {e}")

n_before = len(bulos)
try:
    for entry in feedparser.parse("https://newtral.es/feed/").entries:
        tags = [t.term for t in entry.get("tags", [])]
        if any(t in NEWTRAL_FAKE_TAGS for t in tags) or entry.get("category","") in NEWTRAL_FAKE_TAGS:
            title = entry.get("title","").strip()
            bulos.append({"source":"newtral","title":title,"claim":title,
                          "link":entry.get("link",""),"date":entry.get("published",now)})
    print(f"[DISINFO] {len(bulos)-n_before} bulos newtral")
except Exception as e:
    print(f"[DISINFO] ERROR newtral: {e}")

if not bulos:
    print("[DISINFO] Sin bulos — abortando"); exit(0)

df_bulos = pd.DataFrame(bulos)
df_bulos["fetched_at"] = now
df_bulos.to_csv(BULOS_DB, index=False)
print(f"[DISINFO] {len(df_bulos)} bulos totales")

news_titles = df_news["title"].fillna("").tolist()
bulo_claims = df_bulos["claim"].fillna("").tolist()

vectorizer = TfidfVectorizer(stop_words=STOPWORDS, max_features=5000, ngram_range=(1,2))
X = vectorizer.fit_transform(news_titles + bulo_claims)
X_news  = X[:len(news_titles)]
X_bulos = X[len(news_titles):]
sim_matrix = cosine_similarity(X_news, X_bulos)

alerts = []
for i in range(len(news_titles)):
    news_source = str(df_news.iloc[i].get("source",""))
    if news_source in EXCLUDE_SOURCES:
        continue
    max_sim_idx = int(np.argmax(sim_matrix[i]))
    max_sim     = float(sim_matrix[i][max_sim_idx])
    if max_sim >= SIMILARITY_THRESHOLD:
        bulo = df_bulos.iloc[max_sim_idx]
        alerts.append({
            "news_title":  news_titles[i],
            "news_source": news_source,
            "news_date":   df_news.iloc[i].get("date",""),
            "news_link":   df_news.iloc[i].get("link",""),
            "bulo_title":  bulo["title"],
            "bulo_source": bulo["source"],
            "bulo_link":   bulo["link"],
            "similarity":  round(max_sim,3),
            "risk_score":  min(100, int(max_sim*200)),
            "detected_at": now
        })

df_alerts = pd.DataFrame(alerts) if alerts else pd.DataFrame(
    columns=["news_title","news_source","news_date","news_link",
             "bulo_title","bulo_source","bulo_link","similarity","risk_score","detected_at"])
if len(df_alerts) > 0:
    df_alerts = df_alerts.sort_values("similarity", ascending=False)
df_alerts.to_csv(OUTPUT, index=False)
print(f"[DISINFO] {len(df_alerts)} alertas generadas")

df_alerts["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), df_alerts], ignore_index=True)
    hist = hist.drop_duplicates(subset=["news_title","bulo_title"], keep="last")
else:
    hist = df_alerts.copy()
hist.to_csv(HISTORY, index=False)
print(f"[DISINFO] Historico: {len(hist)} alertas acumuladas")

high_risk = df_alerts[df_alerts["risk_score"] >= 60] if len(df_alerts) > 0 else pd.DataFrame()
if len(high_risk) > 0 and os.path.exists(EMAIL_CFG):
    try:
        with open(EMAIL_CFG) as f:
            ecfg = yaml.safe_load(f)
        body = f"Alertas desinformacion — {now}\nTotal: {len(df_alerts)} | Alto riesgo: {len(high_risk)}\n\n"
        for _, row in high_risk.head(5).iterrows():
            body += f"[{row['risk_score']}] {row['news_source']}: {row['news_title'][:80]}\n"
            body += f"  Bulo: {row['bulo_title'][:80]}\n  {row['bulo_link']}\n\n"
        msg = MIMEText(body)
        msg["Subject"] = f"[narrative-radar] {len(high_risk)} alertas desinformacion — {now}"
        msg["From"] = ecfg["from"]; msg["To"] = ecfg["to"]
        with smtplib.SMTP(ecfg["smtp_host"], 587) as s:
            s.ehlo(); s.starttls(); s.login(ecfg["user"], ecfg["password"]); s.send_message(msg)
        print(f"[DISINFO] Email enviado ({len(high_risk)} alto riesgo)")
    except Exception as e:
        print(f"[DISINFO] Email error: {e}")
print("[DISINFO] Completado.")
