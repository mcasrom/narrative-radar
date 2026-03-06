#!/usr/bin/env python3

import feedparser
import pandas as pd
from datetime import datetime

feeds = {

"rtve": "https://www.rtve.es/rss/noticias.xml",
"elpais": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
"elmundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
"abc": "https://www.abc.es/rss/feeds/abcPortada.xml",
"lavanguardia": "https://www.lavanguardia.com/rss/home.xml"

}

news = []

for source, url in feeds.items():

    feed = feedparser.parse(url)

    for entry in feed.entries:

        news.append({
            "source": source,
            "title": entry.title,
            "date": entry.published if "published" in entry else "",
            "link": entry.link
        })

df = pd.DataFrame(news)

df["collected_at"] = datetime.now()

df.to_csv("../data/raw/news.csv", index=False)

print("Noticias recolectadas:", len(df))
