#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_rss.py
Recolecta noticias reales de medios españoles vía RSS y genera CSV para el dashboard.
Compatible con Odroid C2 / DietPi.
Fuentes cargadas dinámicamente desde config/sources.yaml
"""
import feedparser
import sqlite3
import pandas as pd
import yaml
from datetime import datetime
import os

# Carpeta para CSV
PROCESSED_DIR = "../data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Base de datos SQLite
DB_PATH = "../data/news.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Crear tabla si no existe
cur.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    link TEXT,
    source TEXT,
    date TEXT
)
""")
conn.commit()

# -------------------------------------------------------
# Cargar fuentes desde config/sources.yaml
# -------------------------------------------------------
config_path = os.path.join(os.path.dirname(__file__), "../config/sources.yaml")
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

RSS_FEEDS = {s["name"]: s["url"] for s in config["sources"]}
print(f"[INFO] {len(RSS_FEEDS)} fuentes cargadas desde sources.yaml")

# -------------------------------------------------------
# Recolección
# -------------------------------------------------------
print("[INFO] Recolectando noticias de RSS...")
for source_name, rss_url in RSS_FEEDS.items():
    try:
        feed = feedparser.parse(rss_url)
        count = 0
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            link = entry.get('link', '').strip()
            date = entry.get('published', '') or entry.get('updated', '')
            if date:
                try:
                    date_obj = datetime(*entry.published_parsed[:6])
                    date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cur.execute(
                "INSERT OR IGNORE INTO news(title, link, source, date) VALUES (?,?,?,?)",
                (title, link, source_name, date)
            )
            count += 1
        print(f"  ✅ {source_name}: {count} entradas procesadas")
    except Exception as e:
        print(f"  ⚠️  {source_name}: error al procesar ({e})")

conn.commit()
print("[INFO] Noticias insertadas en SQLite correctamente.")

# Generar CSV para dashboard
df = pd.read_sql_query("SELECT title, link, source, date FROM news ORDER BY date DESC", conn)
csv_path = os.path.join(PROCESSED_DIR, "news_summary.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"[INFO] CSV generado en {csv_path} ({len(df)} registros)")

conn.close()
print("[INFO] Recolección de noticias finalizada.")
