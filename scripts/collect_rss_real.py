#!/usr/bin/env python3
# collect_rss_real.py
# Recolecta noticias de fuentes RSS y genera CSVs para el dashboard

import os
import feedparser
import pandas as pd
import sqlite3
from datetime import datetime

# -----------------------------
# Configuración de directorios
# -----------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
os.makedirs(base_dir, exist_ok=True)
db_path = os.path.join(base_dir, "news.db")

# -----------------------------
# Lista de RSS
# -----------------------------
rss_feeds = {
    "El País": "https://elpais.com/rss/elpais/portada.xml",
    "ABC": "https://www.abc.es/rss/feeds/abcPortada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/mvc/feed/rss/home",
    "RTVE": "https://www.rtve.es/rss/",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml"
}

# -----------------------------
# Conectar a SQLite
# -----------------------------
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT,
    published TEXT,
    source TEXT,
    summary TEXT,
    ingestion_ts TEXT
)
''')
conn.commit()

# -----------------------------
# Función de ingestión RSS
# -----------------------------
def ingest_feed(name, url):
    feed = feedparser.parse(url)
    ingested = 0
    for entry in feed.entries:
        title = entry.get('title', '')
        link = entry.get('link', '')
        published = entry.get('published', '')
        summary = entry.get('summary', '')
        ingestion_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Evitar duplicados por link
        cursor.execute("SELECT COUNT(*) FROM news WHERE link=?", (link,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
            INSERT INTO news (title, link, published, source, summary, ingestion_ts)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, link, published, name, summary, ingestion_ts))
            ingested += 1
    conn.commit()
    return ingested

# -----------------------------
# Recolectar todas las fuentes
# -----------------------------
total_ingested = 0
for name, url in rss_feeds.items():
    count = ingest_feed(name, url)
    print(f"[INFO] {count} noticias nuevas de {name}")
    total_ingested += count

# -----------------------------
# Exportar CSV para dashboard
# -----------------------------
df_news = pd.read_sql_query("SELECT * FROM news ORDER BY published DESC", conn)
csv_path = os.path.join(base_dir, "news_summary.csv")
df_news.to_csv(csv_path, index=False)

print(f"✅ Total noticias ingresadas: {total_ingested}")
print(f"✅ CSV actualizado en {csv_path}")
conn.close()
