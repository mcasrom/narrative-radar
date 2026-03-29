import json, sqlite3
from datetime import datetime
from pathlib import Path

db   = Path.home() / "narrative-radar/data/news.db"
conn = sqlite3.connect(str(db))
total   = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]
sources = conn.execute("SELECT COUNT(DISTINCT source) FROM news").fetchone()[0]
conn.close()

meta = {
    "last_ingestion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_news":     total,
    "sources":        sources,
    "generated_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}
p = Path.home() / "narrative-radar/data/processed/metadata.json"
json.dump(meta, open(p, "w"), indent=2)
print(f"[metadata] {meta}")
