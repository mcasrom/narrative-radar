#!/usr/bin/env python3
"""
geo_analysis.py
Análisis geográfico — menciones de CCAA en titulares.
"""
import pandas as pd
import os
from datetime import datetime

BASE    = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT   = os.path.join(BASE, "data/processed/news_summary.csv")
OUTPUT  = os.path.join(BASE, "data/processed/geo_summary.csv")
HISTORY = os.path.join(BASE, "data/processed/geo_history.csv")

# Diccionario topónimos → CCAA con código ISO para plotly
CCAA_TOPONYMS = {
    "Andalucía":           {"code":"ES-AN","terms":["andalucía","andalucia","sevilla","málaga","malaga","granada","córdoba","cordoba","huelva","jaén","jaen","almería","almeria","cádiz","cadiz"]},
    "Aragón":              {"code":"ES-AR","terms":["aragón","aragon","zaragoza","huesca","teruel"]},
    "Asturias":            {"code":"ES-AS","terms":["asturias","oviedo","gijón","gijon"]},
    "Baleares":            {"code":"ES-IB","terms":["baleares","mallorca","ibiza","menorca","palma"]},
    "Canarias":            {"code":"ES-CN","terms":["canarias","tenerife","gran canaria","las palmas","santa cruz"]},
    "Cantabria":           {"code":"ES-CB","terms":["cantabria","santander"]},
    "Castilla-La Mancha":  {"code":"ES-CM","terms":["castilla-la mancha","toledo","albacete","cuenca","guadalajara","ciudad real"]},
    "Castilla y León":     {"code":"ES-CL","terms":["castilla y león","castilla y leon","valladolid","burgos","salamanca","segovia","ávila","avila","soria","zamora","palencia","león","leon"]},
    "Cataluña":            {"code":"ES-CT","terms":["cataluña","cataluna","catalunya","barcelona","tarragona","girona","lleida","gerona"]},
    "Extremadura":         {"code":"ES-EX","terms":["extremadura","badajoz","cáceres","caceres","mérida","merida"]},
    "Galicia":             {"code":"ES-GA","terms":["galicia","santiago","vigo","coruña","coruna","pontevedra","lugo","ourense"]},
    "La Rioja":            {"code":"ES-RI","terms":["rioja","logroño","logrono"]},
    "Madrid":              {"code":"ES-MD","terms":["madrid","alcalá","alcala","leganés","leganes","móstoles","mostoles","getafe"]},
    "Murcia":              {"code":"ES-MC","terms":["murcia","cartagena","lorca"]},
    "Navarra":             {"code":"ES-NC","terms":["navarra","pamplona","tudela"]},
    "País Vasco":          {"code":"ES-PV","terms":["país vasco","pais vasco","euskadi","bilbao","donostia","san sebastián","san sebastian","vitoria","gasteiz"]},
    "Comunidad Valenciana":{"code":"ES-VC","terms":["valencia","valenciana","alicante","castellón","castellon","elche","torrevieja"]},
    "Ceuta":               {"code":"ES-CE","terms":["ceuta"]},
    "Melilla":             {"code":"ES-ML","terms":["melilla"]},
}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
now = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"[GEO] {now} — Iniciando análisis geográfico")

try:
    df = pd.read_csv(INPUT)
    titles = df["title"].fillna("").str.lower()
    print(f"[GEO] {len(df)} noticias analizadas")
except Exception as e:
    print(f"[GEO] ERROR: {e}"); exit(1)

records = []
for ccaa, data in CCAA_TOPONYMS.items():
    pattern = "|".join(data["terms"])
    mask    = titles.str.contains(pattern, regex=True, na=False)
    count   = int(mask.sum())
    # Top fuentes que mencionan esta CCAA
    top_sources = df[mask]["source"].value_counts().head(3).to_dict() if count > 0 else {}
    # Top titulares
    top_titles  = df[mask]["title"].head(3).tolist() if count > 0 else []
    records.append({
        "ccaa":        ccaa,
        "code":        data["code"],
        "mentions":    count,
        "top_sources": str(top_sources),
        "top_titles":  " | ".join(top_titles),
        "last_update": now
    })

result = pd.DataFrame(records).sort_values("mentions", ascending=False)
result.to_csv(OUTPUT, index=False)

# Histórico
result["cycle"] = now
if os.path.exists(HISTORY):
    hist = pd.concat([pd.read_csv(HISTORY), result], ignore_index=True)
    hist = hist.drop_duplicates(subset=["ccaa","cycle"], keep="last")
else:
    hist = result.copy()
hist.to_csv(HISTORY, index=False)

print("\n=== MENCIONES POR CCAA ===")
for _, row in result[result["mentions"]>0].iterrows():
    bar = "█" * min(30, int(row["mentions"]/5))
    print(f"  {row['ccaa']:<25} {row['mentions']:>4} {bar}")
print(f"\n[GEO] Completado — {result['mentions'].sum()} menciones totales")
