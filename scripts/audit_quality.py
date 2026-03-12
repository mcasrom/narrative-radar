#!/usr/bin/env python3
# ============================================================
# audit_quality.py — Auditoría & Auto-corrección
# Narrative Radar España
# ============================================================
# Ejecuta validaciones sobre todos los CSVs del pipeline:
#   1. Validación de datos (vacíos, NaN, fechas fuera de rango)
#   2. Coherencia narrativa (keywords vs clusters)
#   3. Detección de fallos RSS (fuentes sin datos en 6h)
#   4. Auto-corrección si score < umbral
#
# Salida: data/processed/audit_quality.csv (histórico)
#         data/processed/audit_quality_latest.csv (último ciclo)
# ============================================================

import os
import sys
import json
import subprocess
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------
BASE      = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
SCRIPTS   = BASE / "scripts"
LOG_FILE  = BASE / "pipeline.log"

NOW       = datetime.now()
CORTE_90  = NOW - timedelta(days=90)
CORTE_6H  = NOW - timedelta(hours=6)

# Umbrales
UMBRAL_FILAS_OK      = 50
UMBRAL_FILAS_WARN    = 10
# CSVs summary que por naturaleza tienen pocas filas — no alertar
CSVS_SUMMARY = {
    "narratives_summary.csv",
    "emotions_summary.csv",
    "sentiment_summary.csv",
    "polarization_summary.csv",
    "government_coverage.csv",
    "diversity_index.csv",
    "geo_summary.csv",
    "audit_global_summary.csv",
}
UMBRAL_FECHAS_OK     = 0.80   # 80% filas dentro de 90d
UMBRAL_FECHAS_WARN   = 0.50
UMBRAL_FUENTES_OK    = 20
UMBRAL_FUENTES_WARN  = 10
UMBRAL_NLP_OK        = 0.60
UMBRAL_NLP_WARN      = 0.40
UMBRAL_GLOBAL_AUTO   = 50     # score global < 50 → auto-corrección

# Mapeo CSV → script que lo regenera
SCRIPT_MAP = {
    "narratives_summary.csv":        "detect_narratives.py",
    "emotions_summary.csv":          "detect_emotions.py",
    "polarization_summary.csv":      "detect_polarization.py",
    "actors_network.csv":            "build_network.py",
    "propagation_summary.csv":       "propagation_analysis.py",
    "trends_summary.csv":            "trends_analysis.py",
    "government_coverage.csv":       "government_coverage.py",
    "mass_media_coverage.csv":       "mass_media_analysis.py",
    "news_summary.csv":              "collect_rss_real.py",
    "sentiment_summary.csv":         "detect_sentiment_nlp.py",
    "personas_summary.csv":          "personas_tracking.py",
    "diversity_index.csv":           "diversity_index.py",
    "geo_summary.csv":               "geo_analysis.py",
    "disinfo_alerts.csv":            "detect_disinfo.py",
    "coordination_alerts.csv":       "detect_coordination.py",
    "keywords_emerging.csv":         "keywords_analysis.py",
    "viral_topics.csv":              "detect_viral.py",
}

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] 🔍 AUDIT: {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def semaforo(score):
    if score >= 75:   return "🟢"
    if score >= 50:   return "🟡"
    return "🔴"


def score_filas(n):
    if n >= UMBRAL_FILAS_OK:   return 100
    if n >= UMBRAL_FILAS_WARN: return 50
    return 0


def score_fechas(pct):
    if pct >= UMBRAL_FECHAS_OK:   return 100
    if pct >= UMBRAL_FECHAS_WARN: return 50
    return 0


def relanzar_script(script_name):
    """Ejecuta el script Python correspondiente para regenerar el CSV."""
    script_path = SCRIPTS / script_name
    if not script_path.exists():
        log(f"⚠️  Script no encontrado: {script_name}")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPTS),
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            log(f"✅ Auto-corrección OK: {script_name}")
            return True
        else:
            log(f"❌ Auto-corrección falló: {script_name} — {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        log(f"⏱️  Timeout en auto-corrección: {script_name}")
        return False
    except Exception as e:
        log(f"❌ Error en auto-corrección: {script_name} — {e}")
        return False


# ------------------------------------------------------------------
# VALIDACIÓN 1 — Datos CSV
# ------------------------------------------------------------------

def validar_csvs():
    resultados = []
    for fname, script in SCRIPT_MAP.items():
        fpath = PROCESSED / fname
        entrada = {
            "modulo": fname.replace(".csv", ""),
            "script": script,
            "existe": fpath.exists(),
            "filas": 0,
            "pct_fechas_recientes": 0.0,
            "pct_nulos": 0.0,
            "score_datos": 0,
            "alerta": "",
            "autocorregido": False,
        }

        if not fpath.exists():
            entrada["alerta"] = "CSV no existe"
            entrada["score_datos"] = 0
            resultados.append(entrada)
            continue

        try:
            df = pd.read_csv(fpath)
            entrada["filas"] = len(df)

            # % nulos
            if len(df) > 0:
                entrada["pct_nulos"] = round(df.isnull().mean().mean(), 3)

            # % fechas recientes
            col_fecha = next((c for c in ["date","last_update","cycle","detected_at"]
                              if c in df.columns), None)
            if col_fecha and len(df) > 0:
                df["_d"] = pd.to_datetime(df[col_fecha], errors="coerce")
                recientes = (df["_d"] >= CORTE_90).sum()
                entrada["pct_fechas_recientes"] = round(recientes / len(df), 3)
            else:
                entrada["pct_fechas_recientes"] = 1.0  # sin col fecha → OK

            # Score
            s_filas  = score_filas(entrada["filas"])
            s_fechas = score_fechas(entrada["pct_fechas_recientes"])
            s_nulos  = 100 if entrada["pct_nulos"] < 0.1 else (50 if entrada["pct_nulos"] < 0.3 else 0)
            entrada["score_datos"] = int((s_filas + s_fechas + s_nulos) / 3)

            # Alertas
            alertas = []
            _csv_name = os.path.basename(entrada.get("csv",""))
            if entrada["filas"] < UMBRAL_FILAS_WARN and _csv_name not in CSVS_SUMMARY:
                alertas.append(f"Pocas filas ({entrada['filas']})")
            if entrada["pct_fechas_recientes"] < UMBRAL_FECHAS_WARN:
                alertas.append(f"Fechas antiguas ({entrada['pct_fechas_recientes']*100:.0f}% recientes)")
            if entrada["pct_nulos"] > 0.3:
                alertas.append(f"Muchos nulos ({entrada['pct_nulos']*100:.0f}%)")
            entrada["alerta"] = " | ".join(alertas)

        except Exception as e:
            entrada["alerta"] = f"Error lectura: {e}"
            entrada["score_datos"] = 0

        resultados.append(entrada)
    return resultados


# ------------------------------------------------------------------
# VALIDACIÓN 2 — Coherencia narrativa
# ------------------------------------------------------------------

def validar_coherencia_nlp():
    resultado = {
        "score_nlp": 100,
        "alerta_nlp": "",
        "top_keywords": [],
        "top_clusters": [],
        "solapamiento": 0.0,
    }

    try:
        news_path = PROCESSED / "news_summary.csv"
        narr_path = PROCESSED / "narratives_summary.csv"
        trend_path = PROCESSED / "trends_summary.csv"

        if not news_path.exists() or not narr_path.exists():
            resultado["alerta_nlp"] = "Faltan archivos para coherencia NLP"
            resultado["score_nlp"] = 50
            return resultado

        # Top keywords de tendencias
        if trend_path.exists():
            df_trend = pd.read_csv(trend_path)
            if "keyword" in df_trend.columns and "count" in df_trend.columns:
                top_kw = set(df_trend.nlargest(10, "count")["keyword"].str.lower().tolist())
                resultado["top_keywords"] = list(top_kw)

        # Top palabras de clusters narrativos
        df_narr = pd.read_csv(narr_path)
        col_label = "cluster_label" if "cluster_label" in df_narr.columns else "cluster"
        if col_label in df_narr.columns:
            texto_clusters = " ".join(df_narr[col_label].astype(str).tolist()).lower()
            palabras_clusters = set(texto_clusters.split())
            resultado["top_clusters"] = list(palabras_clusters)[:20]

            # Solapamiento
            if resultado["top_keywords"] and palabras_clusters:
                solapamiento = len(top_kw & palabras_clusters) / max(len(top_kw), 1)
                resultado["solapamiento"] = round(solapamiento, 3)

                if solapamiento >= UMBRAL_NLP_OK:
                    resultado["score_nlp"] = 100
                elif solapamiento >= UMBRAL_NLP_WARN:
                    resultado["score_nlp"] = 60
                    resultado["alerta_nlp"] = f"Coherencia NLP moderada ({solapamiento*100:.0f}%)"
                else:
                    resultado["score_nlp"] = 20
                    resultado["alerta_nlp"] = f"Baja coherencia NLP ({solapamiento*100:.0f}%) — clusters desactualizados"

    except Exception as e:
        resultado["alerta_nlp"] = f"Error coherencia NLP: {e}"
        resultado["score_nlp"] = 50

    return resultado


# ------------------------------------------------------------------
# VALIDACIÓN 3 — Fallos RSS
# ------------------------------------------------------------------

def validar_fuentes_rss():
    resultado = {
        "fuentes_total": 0,
        "fuentes_activas_6h": 0,
        "fuentes_fallidas": [],
        "score_rss": 100,
        "alerta_rss": "",
    }

    try:
        audit_path = PROCESSED / "audit_sources.csv"
        if not audit_path.exists():
            resultado["alerta_rss"] = "audit_sources.csv no encontrado"
            resultado["score_rss"] = 50
            return resultado

        df = pd.read_csv(audit_path)
        resultado["fuentes_total"] = len(df)

        if "timestamp" in df.columns:
            df["_ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
            activas = df[df["_ts"] >= CORTE_6H]
            resultado["fuentes_activas_6h"] = len(activas)

            fallidas = df[df["_ts"] < CORTE_6H]
            if "source" in fallidas.columns:
                resultado["fuentes_fallidas"] = fallidas["source"].tolist()[:10]
        else:
            # Sin timestamp, verificar status
            if "status" in df.columns:
                activas = df[df["status"] == "OK"]
                resultado["fuentes_activas_6h"] = len(activas)
                fallidas = df[df["status"] != "OK"]
                if "source" in fallidas.columns:
                    resultado["fuentes_fallidas"] = fallidas["source"].tolist()[:10]

        n = resultado["fuentes_activas_6h"]
        if n >= UMBRAL_FUENTES_OK:
            resultado["score_rss"] = 100
        elif n >= UMBRAL_FUENTES_WARN:
            resultado["score_rss"] = 60
            resultado["alerta_rss"] = f"Solo {n} fuentes activas en últimas 6h"
        else:
            resultado["score_rss"] = 20
            resultado["alerta_rss"] = f"⚠️ Solo {n} fuentes activas — posible fallo RSS masivo"

    except Exception as e:
        resultado["alerta_rss"] = f"Error validación RSS: {e}"
        resultado["score_rss"] = 50

    return resultado


# ------------------------------------------------------------------
# AUTO-CORRECCIÓN
# ------------------------------------------------------------------

def autocorregir(resultados_csv, score_global):
    acciones = []
    if score_global >= UMBRAL_GLOBAL_AUTO:
        return acciones

    log(f"🔧 Score global {score_global} < {UMBRAL_GLOBAL_AUTO} — iniciando auto-corrección")

    for r in resultados_csv:
        if r["score_datos"] < 50 and r["script"] and not r["autocorregido"]:
            log(f"🔧 Relanzando {r['script']} para {r['modulo']}")
            ok = relanzar_script(r["script"])
            r["autocorregido"] = ok
            acciones.append({
                "modulo": r["modulo"],
                "script": r["script"],
                "resultado": "✅ OK" if ok else "❌ Falló",
                "timestamp": NOW.strftime("%Y-%m-%d %H:%M:%S"),
            })

    return acciones


# ------------------------------------------------------------------
# GUARDAR RESULTADOS
# ------------------------------------------------------------------

def guardar_resultados(resultados_csv, nlp, rss, acciones, score_global):
    ts = NOW.strftime("%Y-%m-%d %H:%M:%S")

    # ── Resumen por módulo ────────────────────────────────────
    rows = []
    for r in resultados_csv:
        rows.append({
            "timestamp":             ts,
            "modulo":                r["modulo"],
            "existe":                r["existe"],
            "filas":                 r["filas"],
            "pct_fechas_recientes":  r["pct_fechas_recientes"],
            "pct_nulos":             r["pct_nulos"],
            "score_datos":           r["score_datos"],
            "alerta":                r["alerta"],
            "autocorregido":         r["autocorregido"],
        })

    df_latest = pd.DataFrame(rows)
    df_latest["score_nlp"]          = nlp["score_nlp"]
    df_latest["score_rss"]          = rss["score_rss"]
    df_latest["score_global"]       = score_global
    df_latest["solapamiento_nlp"]   = nlp["solapamiento"]
    df_latest["fuentes_activas_6h"] = rss["fuentes_activas_6h"]
    df_latest["fuentes_total"]      = rss["fuentes_total"]
    df_latest["alerta_nlp"]         = nlp["alerta_nlp"]
    df_latest["alerta_rss"]         = rss["alerta_rss"]

    # Guardar latest
    latest_path = PROCESSED / "audit_quality_latest.csv"
    df_latest.to_csv(latest_path, index=False)

    # Guardar histórico (acumular, ventana 90 días)
    history_path = PROCESSED / "audit_quality_history.csv"
    if history_path.exists():
        df_hist = pd.read_csv(history_path)
        df_hist = pd.concat([df_hist, df_latest], ignore_index=True)
        df_hist["_d"] = pd.to_datetime(df_hist["timestamp"], errors="coerce")
        df_hist = df_hist[df_hist["_d"] >= CORTE_90.strftime("%Y-%m-%d")]
        df_hist = df_hist.drop(columns=["_d"])
    else:
        df_hist = df_latest

    df_hist.to_csv(history_path, index=False)

    # Guardar acciones de auto-corrección
    if acciones:
        acc_path = PROCESSED / "audit_autocorrections.csv"
        df_acc = pd.DataFrame(acciones)
        if acc_path.exists():
            df_acc = pd.concat([pd.read_csv(acc_path), df_acc], ignore_index=True)
        df_acc.to_csv(acc_path, index=False)

    # Resumen global
    resumen_path = PROCESSED / "audit_global_summary.csv"
    pd.DataFrame([{
        "timestamp":        ts,
        "score_global":     score_global,
        "score_datos_medio": df_latest["score_datos"].mean().round(1),
        "score_nlp":        nlp["score_nlp"],
        "score_rss":        rss["score_rss"],
        "modulos_ok":       (df_latest["score_datos"] >= 75).sum(),
        "modulos_warn":     ((df_latest["score_datos"] >= 50) & (df_latest["score_datos"] < 75)).sum(),
        "modulos_error":    (df_latest["score_datos"] < 50).sum(),
        "autocorrecciones": len(acciones),
        "alerta_nlp":       nlp["alerta_nlp"],
        "alerta_rss":       rss["alerta_rss"],
    }]).to_csv(resumen_path, index=False)

    log(f"Score global: {score_global}/100 {semaforo(score_global)} — "
        f"Módulos OK:{(df_latest['score_datos']>=75).sum()} "
        f"WARN:{((df_latest['score_datos']>=50)&(df_latest['score_datos']<75)).sum()} "
        f"ERR:{(df_latest['score_datos']<50).sum()}")

    return df_latest


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def main():
    log("═" * 50)
    log("Iniciando auditoría de calidad del pipeline")

    # 1. Validar CSVs
    log("1/3 Validando CSVs...")
    resultados_csv = validar_csvs()

    # 2. Coherencia NLP
    log("2/3 Verificando coherencia narrativa...")
    nlp = validar_coherencia_nlp()

    # 3. Fuentes RSS
    log("3/3 Verificando fuentes RSS...")
    rss = validar_fuentes_rss()

    # Score global
    score_datos_medio = np.mean([r["score_datos"] for r in resultados_csv])
    score_global = int((score_datos_medio * 0.5 + nlp["score_nlp"] * 0.25 + rss["score_rss"] * 0.25))

    # 4. Auto-corrección si necesario
    acciones = autocorregir(resultados_csv, score_global)

    # Si hubo auto-corrección, recalcular score
    if acciones:
        log("Recalculando score tras auto-corrección...")
        resultados_csv = validar_csvs()
        score_datos_medio = np.mean([r["score_datos"] for r in resultados_csv])
        score_global = int((score_datos_medio * 0.5 + nlp["score_nlp"] * 0.25 + rss["score_rss"] * 0.25))

    # 5. Guardar
    guardar_resultados(resultados_csv, nlp, rss, acciones, score_global)

    log(f"Auditoría completada — Score: {score_global}/100 {semaforo(score_global)}")
    log("═" * 50)

    return score_global


if __name__ == "__main__":
    main()
