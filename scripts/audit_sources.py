#!/usr/bin/env python3
"""
audit_sources.py
Audita las fuentes RSS del sources.yaml y envia alerta por email si hay caidas.
Se ejecuta via cron tras cada ciclo de ingestión.
"""
import feedparser
import yaml
import os
import socket
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.abspath(os.path.join(BASE, "../config/sources.yaml"))
AUDIT_LOG = os.path.abspath(os.path.join(BASE, "../data/processed/audit_sources.csv"))
EMAIL_CFG = os.path.abspath(os.path.join(BASE, "../config/email.yaml"))

socket.setdefaulttimeout(10)

# ── Cargar fuentes ───────────────────────────────────────
with open(CONFIG, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

now = datetime.now().strftime("%Y-%m-%d %H:%M")
results = []

print(f"[AUDIT] {now} — Auditando {len(config['sources'])} fuentes...")
for s in config["sources"]:
    try:
        feed = feedparser.parse(s["url"])
        n = len(feed.entries)
        status = "OK" if n > 0 else "CAIDA"
    except Exception as e:
        n = 0
        status = "ERROR"
    results.append({"source": s["name"], "url": s["url"], "entries": n, "status": status, "timestamp": now})
    icon = "✅" if status == "OK" else "❌"
    print(f"  {icon} {s['name']:<25} {n:>6} entradas  {status}")

# ── Guardar log CSV ──────────────────────────────────────
import pandas as pd
df_new = pd.DataFrame(results)
if os.path.exists(AUDIT_LOG):
    df_hist = pd.read_csv(AUDIT_LOG)
    df_hist = pd.concat([df_hist, df_new], ignore_index=True)
else:
    df_hist = df_new
df_hist.to_csv(AUDIT_LOG, index=False)

# ── Resumen ──────────────────────────────────────────────
ok = [r for r in results if r["status"] == "OK"]
caidas = [r for r in results if r["status"] != "OK"]
print(f"\n[AUDIT] Resumen: {len(ok)} OK / {len(caidas)} caídas")

# ── Email si hay caídas ──────────────────────────────────
if caidas and os.path.exists(EMAIL_CFG):
    try:
        with open(EMAIL_CFG, "r") as f:
            ecfg = yaml.safe_load(f)

        body = f"Auditoría RSS — {now}\n\n"
        body += f"Fuentes OK: {len(ok)}\n"
        body += f"Fuentes caídas: {len(caidas)}\n\n"
        body += "CAÍDAS:\n"
        for r in caidas:
            body += f"  - {r['source']}: {r['url']}\n"
        body += "\n-- narrative-radar / Odroid-C2"

        msg = MIMEText(body)
        msg["Subject"] = f"[narrative-radar] {len(caidas)} fuentes caídas — {now}"
        msg["From"] = ecfg["from"]
        msg["To"] = ecfg["to"]

        with smtplib.SMTP_SSL(ecfg["smtp_host"], ecfg.get("smtp_port", 465)) as server:
            server.login(ecfg["user"], ecfg["password"])
            server.send_message(msg)
        print(f"[AUDIT] Email de alerta enviado a {ecfg['to']}")
    except Exception as e:
        print(f"[AUDIT] Email no enviado: {e}")
elif caidas:
    print("[AUDIT] Sin config email — omitiendo alerta")
