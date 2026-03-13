#!/usr/bin/env python3
"""
kofi_notify.py
Comprueba nuevos suscriptores de Ko-fi y envía email con password automáticamente.
Ejecutar cada 15 min via cron:
  */15 * * * * /home/dietpi/narrative-radar/env/bin/python3 /home/dietpi/narrative-radar/scripts/kofi_notify.py
"""

import os
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configuración ─────────────────────────────────────────────────
KOFI_TOKEN     = "acac8ff6-906a-4a3e-8039-5b5e3cc305ce"
GMAIL_USER     = "mcasrom@gmail.com"
GMAIL_PASSWORD = "yuuwwsjibbuzalnc"
PASSWORD_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/app_password.txt")

def get_app_password():
    try:
        with open(PASSWORD_FILE) as f:
            return f.read().strip()
    except:
        return "CMNE-MARZO-2026"  # fallback si no existe el fichero
APP_URL        = "https://fake-news-narrative.streamlit.app/"

# Archivo para recordar a quién ya se le envió el email
SENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/kofi_sent.json")

# ── Cargar enviados previos ───────────────────────────────────────
def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE) as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    os.makedirs(os.path.dirname(SENT_FILE), exist_ok=True)
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent), f)

# ── Consultar suscriptores Ko-fi ──────────────────────────────────
def get_kofi_subscribers():
    url = f"https://ko-fi.com/api/v1/subscriptions?token={KOFI_TOKEN}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"[KOFI] Error {resp.status_code}: {resp.text[:100]}")
            return []
    except Exception as e:
        print(f"[KOFI] Error conectando: {e}")
        return []

# ── Enviar email con password ─────────────────────────────────────
def send_password_email(to_email, name=""):
    APP_PASSWORD = get_app_password()
    subject = "🔐 Tu acceso a Narrative Radar"
    body = f"""Hola{' ' + name if name else ''},

Gracias por suscribirte a Narrative Radar.

Tu acceso premium está activo. Estos son tus datos:

  🌐 App: {APP_URL}
  🔑 Password: {APP_PASSWORD}

Con tu suscripción tienes acceso a:
  • 19 módulos completos
  • Briefing PDF diario
  • Alertas en tiempo real
  • Análisis de narrativas y fake news

Introduce la password en el panel izquierdo de la app.

Si tienes cualquier problema responde a este email.

Saludos,
Narrative Radar
"""
    msg = MIMEMultipart()
    msg["From"]    = GMAIL_USER
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[EMAIL] ✅ Enviado a {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL] ❌ Error enviando a {to_email}: {e}")
        return False

# ── Main ──────────────────────────────────────────────────────────
def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[KOFI] {now} — Comprobando suscriptores...")

    sent = load_sent()
    subscribers = get_kofi_subscribers()

    if not subscribers:
        print("[KOFI] Sin suscriptores o error en API.")
        return

    print(f"[KOFI] {len(subscribers)} suscriptores encontrados")
    new_count = 0

    for sub in subscribers:
        email = sub.get("email") or sub.get("Email") or ""
        name  = sub.get("name")  or sub.get("Name")  or ""

        if not email:
            continue

        if email not in sent:
            print(f"[KOFI] Nuevo suscriptor: {email}")
            if send_password_email(email, name):
                sent.add(email)
                new_count += 1

    save_sent(sent)
    print(f"[KOFI] {new_count} emails nuevos enviados. Total registrados: {len(sent)}")

if __name__ == "__main__":
    main()
