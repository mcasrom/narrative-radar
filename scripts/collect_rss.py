#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
collect_rss.py
Recolecta noticias reales de medios españoles vía RSS y genera CSV para el dashboard.
Compatible con Odroid C2 / DietPi.
"""

import feedparser
import sqlite3
import pandas as pd
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

# Fuentes RSS españolas
RSS_FEEDS = {
    "RTVE": "https://www.rtve.es/rss/",
    "El Pais": "https://elpais.com/rss/elpais/portada.xml",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "ABC": "https://www.abc.es/rss/feeds/abcPortada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/mvc/feed/rss/home",
    "Publico": "https://www.publico.es/rss.xml"
}

print("[INFO] Recolectando noticias de RSS...")

for source_name, rss_url in RSS_FEEDS.items():
    feed = feedparser.parse(rss_url)
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

        # Insertar en SQLite evitando duplicados
        cur.execute(
            "INSERT OR IGNORE INTO news(title, link, source, date) VALUES (?,?,?,?)",
            (title, link, source_name, date)
        )

conn.commit()
print("[INFO] Noticias insertadas en SQLite correctamente.")

# Generar CSV para dashboard
df = pd.read_sql_query("SELECT title, link, source, date FROM news ORDER BY date DESC", conn)
csv_path = os.path.join(PROCESSED_DIR, "news_summary.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"[INFO] CSV generado en {csv_path}")

conn.close()
print("[INFO] Recolección de noticias finalizada.")
