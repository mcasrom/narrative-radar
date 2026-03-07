#!/usr/bin/env python3
"""
daily_briefing.py
Genera y envía un briefing diario a las 07:00 consolidando
todos los módulos del pipeline en un email ejecutivo.
"""
import pandas as pd
import numpy as np
import os
import yaml
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE      = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PROC      = os.path.join(BASE, "data/processed")
EMAIL_CFG = os.path.join(BASE, "config/email.yaml")

now     = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
DIAS = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
        "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
MESES = {"January":"enero","February":"febrero","March":"marzo","April":"abril",
         "May":"mayo","June":"junio","July":"julio","August":"agosto",
         "September":"septiembre","October":"octubre","November":"noviembre","December":"diciembre"}
today = f"{DIAS[now.strftime('%A')]} {now.strftime('%d')} de {MESES[now.strftime('%B')]} de {now.strftime('%Y')}"

print(f"[BRIEFING] {now_str} — Generando briefing diario")

def load(fname, **kwargs):
    path = os.path.join(PROC, fname)
    try:
        return pd.read_csv(path, **kwargs) if os.path.exists(path) else pd.DataFrame()
    except:
        return pd.DataFrame()

def section(title, content):
    return f"\n{'═'*60}\n  {title}\n{'═'*60}\n{content}\n"

lines = []
lines.append(f"CENTRO DE MANDO NARRATIVO ESPAÑA — BRIEFING DIARIO")
lines.append(f"{today}")
lines.append(f"Generado: {now_str} | Odroid-C2 / narrative-radar")
lines.append("═"*60)

# ── 1. Noticias del día ──────────────────────────────────────────
df_news = load("news_summary.csv", parse_dates=["date"])
if not df_news.empty:
    df_news["date"] = pd.to_datetime(df_news["date"], errors="coerce")
    ayer    = now - timedelta(hours=24)
    recents = df_news[df_news["date"] >= ayer]
    fuentes_activas = recents["source"].nunique() if not recents.empty else 0
    body = f"  Noticias últimas 24h:  {len(recents):>5}\n"
    body += f"  Fuentes activas:       {fuentes_activas:>5}\n"
    body += f"  Total histórico:       {len(df_news):>5}\n"
    if not recents.empty:
        top_src = recents["source"].value_counts().head(3)
        body += f"  Top fuentes:           {', '.join([f'{s}({n})' for s,n in top_src.items()])}\n"
    lines.append(section("📰 ACTIVIDAD INFORMATIVA", body))

# ── 2. Narrativas coordinadas ────────────────────────────────────
df_coord = load("coordination_alerts.csv")
if not df_coord.empty:
    high = df_coord[df_coord["coord_score"] >= 50]
    body = f"  Eventos detectados:    {len(df_coord):>5}\n"
    body += f"  Alto score (≥50):      {len(high):>5}\n"
    if not high.empty:
        body += "\n  TOP NARRATIVAS COORDINADAS:\n"
        for _, row in high.head(3).iterrows():
            body += f"  [{row['coord_score']:>3}] {row['n_sources']} fuentes — {str(row['representative'])[:70]}\n"
            body += f"       Fuentes: {str(row['sources'])[:60]}\n"
    lines.append(section("🔴 NARRATIVAS COORDINADAS", body))

# ── 3. Desinformación ────────────────────────────────────────────
df_dis = load("disinfo_alerts.csv")
if not df_dis.empty:
    high = df_dis[df_dis["risk_score"] >= 60]
    body = f"  Alertas totales:       {len(df_dis):>5}\n"
    body += f"  Alto riesgo (≥60):     {len(high):>5}\n"
    if not high.empty:
        body += "\n  ALERTAS DE ALTO RIESGO:\n"
        for _, row in high.head(3).iterrows():
            body += f"  [{row['risk_score']:>3}] {row['news_source']}: {str(row['news_title'])[:65]}\n"
            body += f"       Bulo: {str(row['bulo_title'])[:65]}\n"
    else:
        body += "\n  ✅ Sin alertas de alto riesgo.\n"
    lines.append(section("⚠️  DESINFORMACIÓN", body))

# ── 4. Temas virales ─────────────────────────────────────────────
df_viral = load("viral_topics.csv")
if not df_viral.empty:
    body = f"  Temas virales:         {len(df_viral):>5}\n"
    if len(df_viral) > 0:
        body += "\n  KEYWORDS EN EXPLOSIÓN:\n"
        for _, row in df_viral.head(5).iterrows():
            body += f"  [{row['viral_score']:>3}] x{row['ratio']:<5} '{row['keyword']}' — {str(row['sources'])[:50]}\n"
    lines.append(section("🔥 TEMAS VIRALES", body))

# ── 5. Personajes políticos ──────────────────────────────────────
df_per = load("personas_summary.csv")
if not df_per.empty:
    df_per = df_per[df_per["mentions"] > 0].sort_values("mentions", ascending=False)
    body = f"  Personajes monitorizados: {len(df_per)}\n\n"
    body += f"  {'Personaje':<16} {'Menciones':>9} {'Sentimiento':>11} {'Pos':>4} {'Neg':>4}\n"
    body += f"  {'-'*50}\n"
    for _, row in df_per.iterrows():
        s = row["sentiment_score"]
        icon = "🟢" if s > 0.1 else "🔴" if s < -0.1 else "⚪"
        body += f"  {icon} {row['persona']:<15} {row['mentions']:>9} {s:>+11.2f} {row['positive']:>4} {row['negative']:>4}\n"
    lines.append(section("👤 PERSONAJES POLÍTICOS", body))

# ── 6. Sentimiento ───────────────────────────────────────────────
df_sent = load("sentiment_summary.csv")
df_src  = load("sentiment_by_source.csv")
if not df_sent.empty:
    total = df_sent["count"].sum()
    body  = ""
    for _, row in df_sent.iterrows():
        pct = row["count"]/total*100 if total > 0 else 0
        bar = "█" * int(pct/5)
        body += f"  {row['sentiment']:<10} {row['count']:>5} ({pct:>5.1f}%) {bar}\n"
    if not df_src.empty:
        body += "\n  MÁS NEGATIVAS:\n"
        for _, row in df_src.sort_values("negativity_pct", ascending=False).head(3).iterrows():
            body += f"  {row['negativity_pct']:>5.1f}% negativo — {row['source']}\n"
    lines.append(section("🧠 SENTIMIENTO NLP", body))

# ── 7. Agenda-setting ────────────────────────────────────────────
df_ag = load("agenda_score.csv")
if not df_ag.empty:
    marcadores = df_ag[df_ag["role"]=="Marcador de agenda"]
    body  = f"  Marcadores de agenda:  {len(marcadores):>5}\n\n"
    body += f"  TOP MARCADORES:\n"
    for _, row in marcadores.head(5).iterrows():
        body += f"  {row['agenda_score']:>5.1f}% — {row['source']}\n"
    lines.append(section("📡 AGENDA-SETTING", body))

# ── 8. Diversidad informativa ────────────────────────────────────
df_div = load("diversity_index.csv")
if not df_div.empty:
    body  = f"  Score medio diversidad: {df_div['diversity_score'].mean():.1f}\n\n"
    body += f"  MÁS DIVERSOS:\n"
    for _, row in df_div.head(3).iterrows():
        body += f"  {row['diversity_score']:>5.1f} — {row['source']}\n"
    body += f"\n  MENOS ORIGINALES:\n"
    for _, row in df_div.tail(3).iterrows():
        body += f"  {row['diversity_score']:>5.1f} — {row['source']}\n"
    lines.append(section("📊 DIVERSIDAD INFORMATIVA", body))

# ── 9. Geografía ─────────────────────────────────────────────────
df_geo = load("geo_summary.csv")
if not df_geo.empty:
    df_geo = df_geo[df_geo["mentions"]>0].sort_values("mentions", ascending=False)
    body  = f"  Total menciones CCAA:  {df_geo['mentions'].sum():>5}\n\n"
    for _, row in df_geo.head(6).iterrows():
        bar = "█" * int(row["mentions"]/10)
        body += f"  {row['ccaa']:<25} {row['mentions']:>4} {bar}\n"
    lines.append(section("🗺️  GEOGRAFÍA", body))

# ── 10. Auditoría de fuentes ─────────────────────────────────────
df_audit = load("audit_sources.csv")
if not df_audit.empty:
    if "checked_at" in df_audit.columns:
        last_cycle = df_audit.sort_values("checked_at").groupby("source").last().reset_index()
    else:
        last_cycle = df_audit
    ok   = len(last_cycle[last_cycle["status"]=="ok"]) if "status" in last_cycle.columns else 0
    fail = len(last_cycle[last_cycle["status"]!="ok"]) if "status" in last_cycle.columns else 0
    body = f"  Fuentes activas:       {len(df_news['source'].unique()) if not df_news.empty else 28:>5}\n"
    body += f"  Último audit OK:       {ok:>5}\n"
    body += f"  Fuentes con problemas: {fail:>5}\n"
    lines.append(section("🔧 ESTADO DE FUENTES", body))

full_text = "\n".join(lines)
full_text += f"\n\n{'═'*60}\nnarrative-radar — Odroid-C2 — {now_str}\n{'═'*60}\n"

print(full_text)

# ── Enviar email ─────────────────────────────────────────────────
if os.path.exists(EMAIL_CFG):
    try:
        with open(EMAIL_CFG) as f:
            ecfg = yaml.safe_load(f)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[narrative-radar] Briefing {now.strftime('%d/%m/%Y')} — {len(df_news[df_news['date'] >= (now-timedelta(hours=24))]) if not df_news.empty else 0} noticias"
        msg["From"] = ecfg["from"]
        msg["To"]   = ecfg["to"]
        msg.attach(MIMEText(full_text, "plain", "utf-8"))

        with smtplib.SMTP(ecfg["smtp_host"], 587) as s:
            s.ehlo(); s.starttls()
            s.login(ecfg["user"], ecfg["password"])
            s.send_message(msg)
        print(f"\n[BRIEFING] Email enviado a {ecfg['to']}")
    except Exception as e:
        print(f"\n[BRIEFING] Email error: {e}")

print("[BRIEFING] Completado.")
