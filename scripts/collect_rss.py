#!/usr/bin/env python3
import feedparser
import sqlite3
import pandas as pd
import yaml
from datetime import datetime
import os

PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed"))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/news.db"))
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("[INFO] Iniciando collect_rss.py")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
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

config_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/sources.yaml"))
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

RSS_FEEDS = {s["name"]: s["url"] for s in config["sources"]}
print(f"[INFO] {len(RSS_FEEDS)} fuentes cargadas desde sources.yaml")

print("[INFO] Recolectando noticias de RSS...")
for source_name, rss_url in RSS_FEEDS.items():
    try:
        feed = feedparser.parse(rss_url)
        count = 0
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            date = entry.get("published", "") or entry.get("updated", "")
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
        print(f"  OK {source_name}: {count} entradas")
    except Exception as e:
        print(f"  ERR {source_name}: {e}")

conn.commit()
df = pd.read_sql_query("SELECT title, link, source, date FROM news ORDER BY date DESC", conn)
csv_path = os.path.join(PROCESSED_DIR, "news_summary.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"[INFO] CSV generado: {csv_path} ({len(df)} registros)")
conn.close()
print("[INFO] Finalizado.")
