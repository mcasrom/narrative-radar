#!/usr/bin/env python3

import pandas as pd
import numpy as np
import nltk

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from datetime import datetime


INPUT_FILE = "../data/processed/news_summary.csv"
OUTPUT_FILE = "../data/processed/narratives_summary.csv"

N_CLUSTERS = 5


# Descargar stopwords si no existen
nltk.download("stopwords")

SPANISH_STOPWORDS = stopwords.words("spanish")


def auto_label_clusters(df):

    labels = {}

    for cluster_id, group in df.groupby("cluster"):

        text = " ".join(group["title"].astype(str))

        vectorizer = TfidfVectorizer(
            stop_words=SPANISH_STOPWORDS,
            max_features=5
        )

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

    except:
        print("No se pudo leer news.csv")
        return


    if "title" not in df.columns:
        print("news.csv no tiene columna title")
        return


    titles = df["title"].fillna("")


    vectorizer = TfidfVectorizer(
        stop_words=SPANISH_STOPWORDS,
        max_features=1000
    )


    X = vectorizer.fit_transform(titles)


    kmeans = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=42,
        n_init=10
    )


    clusters = kmeans.fit_predict(X)

    df["cluster"] = clusters


    labels = auto_label_clusters(df)

    df["cluster_label"] = df["cluster"].map(labels)


    pca = PCA(n_components=2)

    coords = pca.fit_transform(X.toarray())

    df["x"] = coords[:, 0]
    df["y"] = coords[:, 1]


    summary = df.groupby(["cluster", "cluster_label"]).size().reset_index(name="count")

    summary["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")


    summary.to_csv(OUTPUT_FILE, index=False)


    print("Narrativas detectadas correctamente")


if __name__ == "__main__":
    main()
