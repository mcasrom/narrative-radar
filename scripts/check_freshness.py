#!/usr/bin/env python3
"""
check_freshness.py — Auditoría de frescura de CSVs en narrative-radar
Detecta archivos congelados, sin actualizar o con pocos datos recientes.
Uso: python3 check_freshness.py
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

PROCESSED = Path("/home/dietpi/narrative-radar/data/processed")
UMBRAL_HORAS = 2       # alerta si el archivo tiene más de N horas sin cambios
UMBRAL_CRITICO = 24    # crítico si supera 24h

# Columnas de fecha conocidas por CSV
DATE_COLS = ["date", "fecha", "cycle", "last_update", "timestamp", "published", "pub_date"]

NOW = datetime.now()

def detectar_col_fecha(df):
    for col in DATE_COLS:
        if col in df.columns:
            return col
    # Buscar cualquier columna con 'date' o 'time' en el nombre
    for col in df.columns:
        if any(k in col.lower() for k in ["date", "fecha", "time", "cycle", "update"]):
            return col
    return None

def analizar_csv(path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {"estado": "❌ ERROR", "detalle": str(e), "horas": None}

    if df.empty:
        return {"estado": "⚠️  VACÍO", "detalle": "0 filas", "horas": None}

    # Fecha de modificación del archivo
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    horas_archivo = (NOW - mtime).total_seconds() / 3600

    # Fecha más reciente en los datos
    col = detectar_col_fecha(df)
    horas_datos = None
    fecha_max = None
    if col:
        try:
            fechas = pd.to_datetime(df[col], errors="coerce", utc=True).dropna()
            if not fechas.empty:
                fecha_max = fechas.max()
                horas_datos = (NOW - fecha_max).total_seconds() / 3600
        except Exception:
            pass

    # Usar la métrica más relevante
    horas = horas_datos if horas_datos is not None else horas_archivo
    fuente = "datos" if horas_datos is not None else "archivo"

    if horas > UMBRAL_CRITICO:
        estado = "🔴 PARADO"
    elif horas > UMBRAL_HORAS:
        estado = "🟡 RETRASO"
    else:
        estado = "🟢 OK"

    detalle = f"{len(df)} filas | último {fuente}: {fecha_max.strftime('%Y-%m-%d %H:%M') if fecha_max else mtime.strftime('%Y-%m-%d %H:%M')} ({horas:.1f}h)"
    return {"estado": estado, "detalle": detalle, "horas": horas}

# ── MAIN ──────────────────────────────────────────────────────────────────────
csvs = sorted(PROCESSED.glob("*.csv"))
resultados = []

for path in csvs:
    if ".bak" in path.name:
        continue
    r = analizar_csv(path)
    resultados.append((path.name, r))

# Ordenar: primero los más problemáticos
resultados.sort(key=lambda x: x[1]["horas"] or 0, reverse=True)

# ── OUTPUT ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"  AUDITORÍA DE FRESCURA — narrative-radar")
print(f"  {NOW.strftime('%Y-%m-%d %H:%M')}  |  umbral aviso: {UMBRAL_HORAS}h  |  crítico: {UMBRAL_CRITICO}h")
print(f"{'='*70}")

parados, retrasos, ok = [], [], []
for nombre, r in resultados:
    linea = f"  {r['estado']}  {nombre:<45} {r['detalle']}"
    if "PARADO" in r["estado"]:
        parados.append(linea)
    elif "RETRASO" in r["estado"]:
        retrasos.append(linea)
    elif "OK" in r["estado"]:
        ok.append(linea)
    else:
        parados.append(linea)  # ERROR/VACÍO

if parados:
    print(f"\n  ── CRÍTICOS ({len(parados)}) ──")
    for l in parados: print(l)

if retrasos:
    print(f"\n  ── RETRASOS ({len(retrasos)}) ──")
    for l in retrasos: print(l)

if ok:
    print(f"\n  ── OK ({len(ok)}) ──")
    for l in ok: print(l)

print(f"\n{'='*70}")
print(f"  Resumen: 🔴 {len(parados)} parados  🟡 {len(retrasos)} retrasos  🟢 {len(ok)} OK")
print(f"{'='*70}\n")
