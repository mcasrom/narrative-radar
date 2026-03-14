#!/usr/bin/env python3
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from datetime import datetime
import os

INPUT_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/news_summary.csv"))
OUTPUT_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/narratives_summary.csv"))
HISTORY_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/processed/narratives_history.csv"))
N_CLUSTERS = 15

nltk.download("stopwords", quiet=True)
SPANISH_STOPWORDS = stopwords.words("spanish")

def auto_label_clusters(df):
    labels = {}
    for cluster_id, group in df.groupby("cluster"):
        text = " ".join(group["title"].astype(str))
        vectorizer = TfidfVectorizer(stop_words=SPANISH_STOPWORDS, max_features=5)
        try:
            X = vectorizer.fit_transform([text])
            words = vectorizer.get_feature_names_out()
            labels[cluster_id] = " ".join(words)
        except:
            labels[cluster_id] = f"cluster_{cluster_id}"
    return labels

def main():
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"No se pudo leer {INPUT_FILE}: {e}"); return

    if "title" not in df.columns:
        print("news_summary.csv no tiene columna title"); return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Usar solo últimos 14 días para narrativas más actuales
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=14)
    df_recent = df[df["date"] >= cutoff].copy()
    if len(df_recent) < 100:
        df_recent = df.copy()
    titles = df_recent["title"].fillna("")
    df = df_recent
    vectorizer = TfidfVectorizer(stop_words=SPANISH_STOPWORDS, max_features=1000)
    X = vectorizer.fit_transform(titles)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    df["cluster"] = clusters

    labels = auto_label_clusters(df)
    df["cluster_label"] = df["cluster"].map(labels)

    pca = PCA(n_components=2)
    coords = pca.fit_transform(X.toarray())
    df["x"] = coords[:, 0]
    df["y"] = coords[:, 1]

    summary = df.groupby(["cluster", "cluster_label"]).size().reset_index(name="count")
    summary["last_update"] = now
    summary.to_csv(OUTPUT_FILE, index=False)

    # Historico acumulativo
    summary["cycle"] = now
    if os.path.exists(HISTORY_FILE):
        hist = pd.read_csv(HISTORY_FILE)
        hist = pd.concat([hist, summary], ignore_index=True)
        hist = hist.drop_duplicates(subset=["cluster_label","cycle"], keep="last")
    else:
        hist = summary.copy()
    hist.to_csv(HISTORY_FILE, index=False)

    print(f"Narrativas detectadas correctamente ({N_CLUSTERS} clusters, historico: {len(hist)} registros)")

if __name__ == "__main__":
    main()
