#!/usr/bin/env python3
"""
daily_briefing_v2.py
Informe diario ejecutivo — v2.0
- Resumen ejecutivo generado por Claude API
- Email HTML rico con tablas y colores
- PDF adjunto con gráficos (matplotlib)
- Comparativa tendencia vs ayer
Autor: M. Castillo <mybloggingnotes@gmail.com>
"""
import os, sys, json, smtplib, base64, io, textwrap
import pandas as pd
import numpy as np
import yaml
import urllib.request, urllib.error
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF

BASE      = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PROC      = os.path.join(BASE, "data/processed")
EMAIL_CFG = os.path.join(BASE, "config/email.yaml")
SUBS_CFG  = os.path.join(BASE, "config/subscribers.yaml")

def load_subscribers():
    """Carga lista de suscriptores activos"""
    try:
        import yaml
        with open(SUBS_CFG) as f:
            cfg = yaml.safe_load(f)
        return [s for s in cfg.get("subscribers", []) if s.get("active", False)]
    except:
        return []
PDF_OUT   = os.path.join(PROC, "briefing_diario.pdf")
HIST_DIR  = os.path.join(PROC, "briefing_history")
os.makedirs(HIST_DIR, exist_ok=True)

now     = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
ayer    = (now - timedelta(days=1)).strftime("%Y-%m-%d")
hoy     = now.strftime("%Y-%m-%d")

DIAS  = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
         "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
MESES = {"January":"enero","February":"febrero","March":"marzo","April":"abril",
         "May":"mayo","June":"junio","July":"julio","August":"agosto",
         "September":"septiembre","October":"octubre","November":"noviembre","December":"diciembre"}
today_str = f"{DIAS[now.strftime('%A')]} {now.strftime('%d')} de {MESES[now.strftime('%B')]} de {now.strftime('%Y')}"

def strip_emoji(text):
    import re
    emoji_pattern = re.compile(
        u"[😀-🙏🌀-🗿"
        u"🚀-🛿🇠-🇿"
        u"✂-➰Ⓜ-🉑"
        u"🤀-🧿─-⯯"
        u"🀄-🃏]+", flags=re.UNICODE)
    return emoji_pattern.sub('', str(text))

print(f"[BRIEFING v2] {now_str} — Iniciando informe diario")

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def load(fname, **kwargs):
    path = os.path.join(PROC, fname)
    try:
        return pd.read_csv(path, **kwargs) if os.path.exists(path) else pd.DataFrame()
    except:
        return pd.DataFrame()

def load_hist_yesterday(fname):
    """Carga CSV del día anterior desde briefing_history."""
    path = os.path.join(HIST_DIR, f"{ayer}_{fname}")
    try:
        return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    except:
        return pd.DataFrame()

def save_snapshot(fname, df):
    """Guarda snapshot del día para comparativa mañana."""
    if df.empty: return
    path = os.path.join(HIST_DIR, f"{hoy}_{fname}")
    df.to_csv(path, index=False)

def delta_str(val, val_prev, fmt=".0f", invert=False):
    """Devuelve string de variación con flecha y color HTML."""
    if val_prev is None or val_prev == 0:
        return ""
    diff = val - val_prev
    pct  = (diff / abs(val_prev)) * 100 if val_prev != 0 else 0
    good = diff > 0
    if invert: good = not good
    color = "#27ae60" if good else "#e74c3c"
    arrow = "▲" if diff > 0 else "▼"
    return f'<span style="color:{color};font-size:0.85em"> {arrow}{abs(pct):.1f}%</span>'

def bar_html(pct, color="#3498db", width=120):
    filled = int(width * pct / 100)
    return f'<span style="display:inline-block;background:{color};width:{filled}px;height:8px;border-radius:3px;vertical-align:middle"></span>'

# ══════════════════════════════════════════════════════════════════
# 1. RECOPILAR DATOS
# ══════════════════════════════════════════════════════════════════
print("[BRIEFING v2] Cargando datos...")

df_news       = load("news_summary.csv", parse_dates=["date"])
df_narr       = load("narratives_summary.csv")
df_coord      = load("coordination_alerts.csv")
df_disinfo    = load("disinfo_alerts.csv")
df_viral      = load("viral_topics.csv")
df_personas   = load("personas_summary.csv")
df_sentiment  = load("sentiment_summary.csv")
df_agenda     = load("agenda_score.csv")
df_diversity  = load("diversity_index.csv")
df_geo        = load("geo_summary.csv")
df_polar      = load("polarization_summary.csv")
df_mass       = load("mass_media_coverage.csv")
df_audit      = load("audit_quality_latest.csv")

# Snapshots ayer para comparativa
df_news_ay    = load_hist_yesterday("news_summary.csv")
df_coord_ay   = load_hist_yesterday("coordination_alerts.csv")
df_disinfo_ay = load_hist_yesterday("disinfo_alerts.csv")
df_viral_ay   = load_hist_yesterday("viral_topics.csv")
df_polar_ay   = load_hist_yesterday("polarization_summary.csv")

# Guardar snapshots hoy
save_snapshot("news_summary.csv", df_news)
save_snapshot("coordination_alerts.csv", df_coord)
save_snapshot("disinfo_alerts.csv", df_disinfo)
save_snapshot("viral_topics.csv", df_viral)
save_snapshot("polarization_summary.csv", df_polar)

# Métricas principales
n_news_hoy  = len(df_news[df_news["date"] >= pd.Timestamp(hoy)]) if not df_news.empty and "date" in df_news else 0
n_news_ay   = len(df_news_ay) if not df_news_ay.empty else None
n_fuentes   = df_news["source"].nunique() if not df_news.empty and "source" in df_news else 0
n_coord     = len(df_coord)
n_coord_ay  = len(df_coord_ay) if not df_coord_ay.empty else None
n_disinfo   = len(df_disinfo)
n_disinfo_ay= len(df_disinfo_ay) if not df_disinfo_ay.empty else None
n_viral     = len(df_viral)
n_viral_ay  = len(df_viral_ay) if not df_viral_ay.empty else None

pol_hoy = df_polar["polarization_index"].mean() if not df_polar.empty and "polarization_index" in df_polar else 0
pol_ay  = df_polar_ay["polarization_index"].mean() if not df_polar_ay.empty and "polarization_index" in df_polar_ay else None

# Score de riesgo informativo global (0-100)
riesgo_components = []
if n_disinfo > 0:
    riesgo_components.append(min(100, n_disinfo * 10))
if n_coord > 0:
    riesgo_components.append(min(100, n_coord * 0.5))
if pol_hoy > 0:
    riesgo_components.append(min(100, pol_hoy * 100))
score_riesgo = int(np.mean(riesgo_components)) if riesgo_components else 0
nivel_riesgo = "🔴 ALTO" if score_riesgo >= 60 else ("🟡 MEDIO" if score_riesgo >= 30 else "🟢 BAJO")

# Score calidad datos pipeline
audit_score = 0
if not df_audit.empty and "global_score" in df_audit.columns:
    audit_score = int(df_audit["global_score"].iloc[0])

print(f"[BRIEFING v2] Datos cargados — noticias:{n_news_hoy} coord:{n_coord} disinfo:{n_disinfo} riesgo:{score_riesgo}")

# ══════════════════════════════════════════════════════════════════
# 2. RESUMEN EJECUTIVO CON CLAUDE API
# ══════════════════════════════════════════════════════════════════
print("[BRIEFING v2] Generando resumen ejecutivo con Claude API...")

def generar_resumen_ia():
    # Construir contexto compacto para la IA
    top_coord = ""
    if not df_coord.empty and "representative" in df_coord.columns:
        top3 = df_coord.nlargest(3, "coord_score")[["representative","coord_score","n_sources"]].values
        top_coord = " | ".join([f"{r[0][:60]} (score:{r[1]:.0f}, {r[2]:.0f} fuentes)" for r in top3])

    top_disinfo = ""
    if not df_disinfo.empty and "news_title" in df_disinfo.columns:
        top3 = df_disinfo.nlargest(3, "risk_score")[["news_source","risk_score","news_title"]].values
        top_disinfo = " | ".join([f"{r[0]}: {r[2][:50]} (riesgo:{r[1]:.0f})" for r in top3])

    top_personas = ""
    if not df_personas.empty and "persona" in df_personas.columns:
        top5 = df_personas.nlargest(5, "mentions")[["persona","mentions","sentiment_score"]].values
        top_personas = " | ".join([f"{r[0]}({r[1]:.0f} menciones, sent:{r[2]:.2f})" for r in top5])

    top_viral = ""
    if not df_viral.empty and "keyword" in df_viral.columns:
        top3 = df_viral.nlargest(3, "viral_score")[["keyword","viral_score","ratio"]].values
        top_viral = " | ".join([f"'{r[0]}' x{r[2]:.1f}" for r in top3])

    top_geo = ""
    if not df_geo.empty and "ccaa" in df_geo.columns:
        top3 = df_geo.nlargest(3, "mentions")[["ccaa","mentions"]].values
        top_geo = " | ".join([f"{r[0]}({r[1]:.0f})" for r in top3])

    contexto = f"""
Fecha: {today_str}
Noticias últimas 24h: {n_news_hoy} (ayer: {n_news_ay or 'N/A'})
Fuentes activas: {n_fuentes}
Score riesgo informativo: {score_riesgo}/100 ({nivel_riesgo})
Polarización media: {pol_hoy:.3f} (ayer: {f'{pol_ay:.3f}' if pol_ay is not None else 'N/A'})

NARRATIVAS COORDINADAS ({n_coord} eventos, {n_coord_ay or 'N/A'} ayer):
{top_coord or 'Sin datos'}

DESINFORMACIÓN ({n_disinfo} alertas):
{top_disinfo or 'Sin alertas'}

TEMAS VIRALES ({n_viral}):
{top_viral or 'Sin virales'}

PERSONAJES MÁS MENCIONADOS:
{top_personas or 'Sin datos'}

GEOGRAFÍA (top CCAA por menciones):
{top_geo or 'Sin datos'}
"""

    prompt = f"""Eres un analista experto en comunicación política y medios de comunicación españoles.
Basándote en los siguientes datos del sistema de monitorización narrativa de España, 
genera un resumen ejecutivo profesional y conciso (máximo 250 palabras) en español.

El resumen debe:
1. Identificar el tema dominante del día y su relevancia política/social
2. Evaluar el riesgo informativo y posibles campañas de desinformación
3. Destacar tendencias significativas vs el día anterior
4. Señalar qué actores políticos están en el foco mediático y por qué
5. Concluir con una valoración del clima informativo general

Datos del día:
{contexto}

Responde SOLO con el texto del resumen ejecutivo, sin títulos ni encabezados adicionales."""

    try:
        import urllib.request
        data = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")

        api_key = os.environ.get("ANTHROPIC_API_KEY","")
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY no configurada")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["content"][0]["text"].strip()
    except Exception as e:
        print(f"[BRIEFING v2] ⚠️ Claude API no disponible: {e}")
        # Fallback: resumen automático sin IA
        return generar_resumen_fallback()

def generar_resumen_fallback():
    partes = []
    partes.append(f"El {today_str} el sistema de monitorización registró {n_news_hoy} noticias de {n_fuentes} fuentes activas.")
    if n_coord > 0:
        partes.append(f"Se detectaron {n_coord} eventos de narrativa coordinada, indicando actividad informativa sincronizada entre medios.")
    if n_disinfo > 0:
        partes.append(f"El detector de desinformación generó {n_disinfo} alertas de alto riesgo.")
    if n_viral > 0:
        partes.append(f"Se identificaron {n_viral} temas virales en explosión.")
    if pol_hoy > 0:
        partes.append(f"El índice de polarización se sitúa en {pol_hoy:.3f}.")
    partes.append(f"Score de riesgo informativo global: {score_riesgo}/100 ({nivel_riesgo}).")
    return " ".join(partes)

resumen_ia = generar_resumen_ia()
print(f"[BRIEFING v2] Resumen IA generado ({len(resumen_ia)} chars)")

# ══════════════════════════════════════════════════════════════════
# 3. GENERAR GRÁFICOS PARA PDF
# ══════════════════════════════════════════════════════════════════
print("[BRIEFING v2] Generando gráficos...")

COLORES = ["#2c3e50","#e74c3c","#3498db","#2ecc71","#f39c12","#9b59b6","#1abc9c","#e67e22"]

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

graficos = {}

# Gráfico 1: Narrativas coordinadas top 10
if not df_coord.empty and "coord_score" in df_coord.columns and "representative" in df_coord.columns:
    fig, ax = plt.subplots(figsize=(10, 4))
    top10 = df_coord.nlargest(10, "coord_score")
    labels = [textwrap.shorten(str(r), width=50, placeholder="...") for r in top10["representative"]]
    bars = ax.barh(range(len(labels)), top10["coord_score"].values, color=COLORES[1], alpha=0.8)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Score de coordinación")
    ax.set_title("Top 10 Narrativas Coordinadas", fontweight="bold", pad=10)
    ax.invert_yaxis()
    for bar, val in zip(bars, top10["coord_score"].values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{val:.0f}", va="center", fontsize=8)
    plt.tight_layout()
    graficos["coord"] = fig_to_base64(fig)
    plt.close(fig)

# Gráfico 2: Sentimiento global (donut)
if not df_sentiment.empty and "sentiment" in df_sentiment.columns and "count" in df_sentiment.columns:
    fig, ax = plt.subplots(figsize=(5, 4))
    colors_sent = {"positivo":"#2ecc71","negativo":"#e74c3c","neutral":"#95a5a6"}
    df_s = df_sentiment.groupby("sentiment")["count"].sum().reset_index()
    colors = [colors_sent.get(s, "#888") for s in df_s["sentiment"]]
    wedges, texts, autotexts = ax.pie(
        df_s["count"], labels=df_s["sentiment"],
        colors=colors, autopct="%1.1f%%",
        pctdistance=0.8, startangle=90,
        wedgeprops=dict(width=0.5)
    )
    for t in autotexts: t.set_fontsize(9)
    ax.set_title("Sentimiento NLP", fontweight="bold")
    plt.tight_layout()
    graficos["sentiment"] = fig_to_base64(fig)
    plt.close(fig)

# Gráfico 3: Personajes — menciones y sentimiento
if not df_personas.empty and "persona" in df_personas.columns and "mentions" in df_personas.columns:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    top8 = df_personas.nlargest(8, "mentions")
    # Menciones
    ax1.barh(top8["persona"], top8["mentions"], color=COLORES[2], alpha=0.8)
    ax1.set_xlabel("Menciones")
    ax1.set_title("Menciones por personaje", fontweight="bold")
    ax1.invert_yaxis()
    # Sentimiento
    colors_s = ["#2ecc71" if s > 0 else "#e74c3c" for s in top8["sentiment_score"]]
    ax2.barh(top8["persona"], top8["sentiment_score"], color=colors_s, alpha=0.8)
    ax2.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax2.set_xlabel("Score sentimiento")
    ax2.set_title("Sentimiento por personaje", fontweight="bold")
    ax2.invert_yaxis()
    plt.tight_layout()
    graficos["personas"] = fig_to_base64(fig)
    plt.close(fig)

# Gráfico 4: Geografía CCAA
if not df_geo.empty and "ccaa" in df_geo.columns and "mentions" in df_geo.columns:
    fig, ax = plt.subplots(figsize=(8, 5))
    top10 = df_geo[df_geo["mentions"] > 0].nlargest(10, "mentions")
    colors_geo = [COLORES[i % len(COLORES)] for i in range(len(top10))]
    bars = ax.bar(top10["ccaa"], top10["mentions"], color=colors_geo, alpha=0.85)
    ax.set_xlabel("Comunidad Autónoma")
    ax.set_ylabel("Menciones")
    ax.set_title("Intensidad informativa por CCAA", fontweight="bold")
    plt.xticks(rotation=30, ha="right", fontsize=8)
    for bar, val in zip(bars, top10["mentions"].values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                str(int(val)), ha="center", fontsize=8)
    plt.tight_layout()
    graficos["geo"] = fig_to_base64(fig)
    plt.close(fig)

# Gráfico 5: Gauge riesgo informativo
fig, ax = plt.subplots(figsize=(5, 3), subplot_kw=dict(polar=True))
theta = np.linspace(0, np.pi, 100)
ax.fill_between(theta[:33], 0.6, 1.0, color="#2ecc71", alpha=0.7)
ax.fill_between(theta[33:66], 0.6, 1.0, color="#f39c12", alpha=0.7)
ax.fill_between(theta[66:], 0.6, 1.0, color="#e74c3c", alpha=0.7)
needle_angle = np.pi * (1 - score_riesgo / 100)
ax.annotate("", xy=(needle_angle, 0.85), xytext=(needle_angle, 0.55),
            arrowprops=dict(arrowstyle="->", color="black", lw=2))
ax.set_ylim(0, 1)
ax.set_theta_zero_location("W")
ax.set_theta_direction(-1)
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.grid(False)
ax.spines["polar"].set_visible(False)
ax.set_title(f"Riesgo Informativo: {score_riesgo}/100\n{nivel_riesgo}", fontweight="bold", pad=15)
plt.tight_layout()
graficos["riesgo"] = fig_to_base64(fig)

# Gráfico tendencias top keywords
try:
    df_trend = pd.read_csv(os.path.join(PROC, "trends_summary.csv"))
    if not df_trend.empty and "keyword" in df_trend.columns and "count" in df_trend.columns:
        top = df_trend.nlargest(15, "count")
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(top["keyword"][::-1], top["count"][::-1], color="#C00000")
        ax.set_xlabel("Frecuencia")
        ax.set_title("Top 15 Keywords del día", fontsize=13, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        graficos["tendencias"] = fig_to_base64(fig)
        plt.close(fig)
except Exception as e:
    print(f"[BRIEFING] Tendencias graf error: {e}")

# Gráfico diversidad fuentes
try:
    df_div = pd.read_csv(os.path.join(PROC, "diversity_index.csv"))
    if not df_div.empty and "source" in df_div.columns and "diversity_score" in df_div.columns:
        top_div = df_div.nlargest(10, "diversity_score")
        fig, ax = plt.subplots(figsize=(8, 4))
        colors = ["#27AE60" if v >= 70 else "#F39C12" if v >= 50 else "#C0392B" for v in top_div["diversity_score"]]
        ax.bar(top_div["source"], top_div["diversity_score"], color=colors)
        ax.set_ylabel("Score diversidad")
        ax.set_title("Índice de Diversidad por Fuente", fontsize=11, fontweight="bold")
        ax.axhline(70, color="green", linestyle="--", alpha=0.5, label="Umbral alto")
        plt.xticks(rotation=30, ha="right", fontsize=8)
        plt.tight_layout()
        graficos["diversidad"] = fig_to_base64(fig)
        plt.close(fig)
except Exception as e:
    print(f"[BRIEFING] Diversidad graf error: {e}")
plt.close(fig)

print(f"[BRIEFING v2] {len(graficos)} gráficos generados")

# ══════════════════════════════════════════════════════════════════
# 4. GENERAR PDF
# ══════════════════════════════════════════════════════════════════
PREVIEW_MODE = True  # True = marca agua PREVIEW, False = PDF completo sin marca
print("[BRIEFING v2] Generando PDF...")

FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard", "DejaVuSans.ttf")

class BriefingPDF(FPDF):
    def __init__(self, preview=False):
        super().__init__()
        self._preview = preview
        if os.path.exists(FONT_PATH):
            self.add_font("DejaVu", style="", fname=FONT_PATH)
            self.add_font("DejaVu", style="B", fname=FONT_PATH)
            self._F = "DejaVu"
        else:
            self._F = "Helvetica"

    def header(self):
        if self._preview:
            self.set_font(self._F, size=48)
            self.set_text_color(220, 220, 220)
            self.rotate(45, x=60, y=160)
            self.text(20, 180, "PREVIEW")
            self.rotate(0)
            self.set_text_color(0, 0, 0)
        self.set_font(self._F, style="B", size=14)
        self.set_fill_color(44, 62, 80)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "CENTRO DE MANDO NARRATIVO ESPANA", fill=True, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font(self._F, size=9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, f"Briefing Diario - {today_str} - {now_str}", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font(self._F, size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"narrative-radar - M.Castillo | mybloggingnotes@gmail.com | Pag. {self.page_no()}", align="C")

    def section_title(self, title, color=(44,62,80)):
        title = title
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font(self._F, style="B", size=10)
        self.cell(0, 7, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def watermark(self, text="PREVIEW"):
        self.set_font(self._F, size=48)
        self.set_text_color(220, 220, 220)
        with self.local_context():
            self.set_xy(30, 120)
            self.rotate(45)
            self.cell(0, 10, text)
            self.rotate(0)
        self.set_text_color(0, 0, 0)

    def body_text(self, text, size=9):
        text = text
        self.set_font(self._F, size=size)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, strip_emoji(text))
        self.ln(2)

    def kpi_row(self, items):
        """items = list of (label, value, delta_str)"""
        w = self.w - 2*self.l_margin
        cw = w / len(items)
        font = "Arial"
        for label, value, delta in items:
            x = self.get_x()
            y = self.get_y()
            self.set_fill_color(245, 247, 250)
            self.rect(x, y, cw-2, 18, "F")
            self.set_font(self._F, style="B", size=14)
            self.set_text_color(44, 62, 80)
            self.set_xy(x, y+1)
            self.cell(cw-2, 8, strip_emoji(str(value)), align="C")
            self.set_font(self._F, size=7)
            self.set_text_color(100, 100, 100)
            self.set_xy(x, y+9)
            self.cell(cw-2, 5, strip_emoji(label), align="C")
            if delta:
                self.set_font(self._F, size=7)
                col = (39, 174, 96) if "▲" in delta else (231, 76, 60)
                self.set_text_color(*col)
                self.set_xy(x, y+14)
                self.cell(cw-2, 4, strip_emoji(delta), align="C")
            self.set_xy(x + cw, y)
        self.ln(20)

    def add_image_b64(self, b64_str, w=180):
        tmp = os.path.join("/tmp", f"brief_img_{id(b64_str)}.png")
        with open(tmp, "wb") as f:
            f.write(base64.b64decode(b64_str))
        self.image(tmp, x=self.l_margin, w=w)
        self.ln(3)
        try: os.remove(tmp)
        except: pass

pdf = BriefingPDF(preview=PREVIEW_MODE)
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ── KPIs principales ──
def _delta_txt(val, val_prev, invert=False):
    if val_prev is None: return ""
    diff = val - val_prev
    pct = abs(diff / val_prev * 100) if val_prev else 0
    arrow = "▲" if diff > 0 else "▼"
    return f"{arrow} {pct:.1f}%"

pdf.kpi_row([
    ("Noticias 24h",    n_news_hoy,   _delta_txt(n_news_hoy, n_news_ay)),
    ("Fuentes activas", n_fuentes,    ""),
    ("Riesgo info.",    f"{score_riesgo}/100", ""),
    ("Calidad pipeline",f"{audit_score}/100",  ""),
])

# ── Resumen ejecutivo IA ──
resumen_ia_pdf = resumen_ia
pdf.section_title("RESUMEN EJECUTIVO (IA)", color=(52, 73, 94))
pdf.body_text(resumen_ia_pdf)

# ── Riesgo gauge ──
if "riesgo" in graficos:
    pdf.section_title("RIESGO INFORMATIVO", color=(192, 57, 43))
    pdf.add_image_b64(graficos["riesgo"], w=80)

# ── Narrativas coordinadas ──
pdf.section_title("NARRATIVAS COORDINADAS", color=(169, 50, 38))
if not df_coord.empty:
    pdf.body_text(f"Eventos detectados: {n_coord}  |  Alto score (>=50): {len(df_coord[df_coord['coord_score']>=50]) if 'coord_score' in df_coord else '?'}")
    if "coord" in graficos:
        pdf.add_image_b64(graficos["coord"], w=180)
    top5 = df_coord.nlargest(5, "coord_score") if "coord_score" in df_coord.columns else df_coord.head(5)
    for _, row in top5.iterrows():
        rep = str(row.get("representative",""))[:80]
        sc  = row.get("coord_score", 0)
        ns  = row.get("n_sources", 0)
        pdf.body_text(strip_emoji(f"[{sc:.0f}] {ns:.0f} fuentes — {rep}"))
else:
    pdf.body_text("Sin narrativas coordinadas detectadas.")

# ── Desinformación ──
pdf.section_title("DESINFORMACION", color=(230, 126, 34))
if not df_disinfo.empty:
    pdf.body_text(f"Alertas: {n_disinfo}  |  Alto riesgo (>=60): {len(df_disinfo[df_disinfo['risk_score']>=60]) if 'risk_score' in df_disinfo else '?'}")
    top5 = df_disinfo.nlargest(5, "risk_score") if "risk_score" in df_disinfo.columns else df_disinfo.head(5)
    for _, row in top5.iterrows():
        src   = str(row.get("news_source",""))
        title = str(row.get("news_title",""))[:70]
        sc    = row.get("risk_score", 0)
        pdf.body_text(strip_emoji(f"[{sc:.0f}] {src}: {title}"))
else:
    pdf.body_text("Sin alertas de desinformación.")

# ── Nueva página: análisis ──
pdf.add_page()

# ── Sentimiento ──
pdf.section_title("SENTIMIENTO NLP", color=(41, 128, 185))
if "sentiment" in graficos:
    pdf.add_image_b64(graficos["sentiment"], w=90)

# ── Personajes ──
pdf.section_title("PERSONAJES POLITICOS", color=(39, 174, 96))
if "personas" in graficos:
    pdf.add_image_b64(graficos["personas"], w=180)
if not df_personas.empty and "persona" in df_personas.columns:
    top8 = df_personas.nlargest(8, "mentions")
    for _, row in top8.iterrows():
        p = str(row.get("persona",""))
        m = row.get("mentions", 0)
        s = row.get("sentiment_score", 0)
        icon = "🟢" if s > 0.05 else ("🔴" if s < -0.05 else "⚪")
        pdf.body_text(strip_emoji(f"{p}: {m:.0f} menciones | sentimiento: {s:.2f}"))

# ── Geografía ──
pdf.section_title("GEOGRAFIA", color=(142, 68, 173))
if "geo" in graficos:
    pdf.add_image_b64(graficos["geo"], w=170)

# ── Virales ──
# ── Tendencias ──
if "tendencias" in graficos:
    pdf.section_title("TOP KEYWORDS DEL DIA", color=(41, 128, 185))
    pdf.add_image_b64(graficos["tendencias"], w=180)

# ── Diversidad ──
if "diversidad" in graficos:
    pdf.section_title("DIVERSIDAD INFORMATIVA", color=(39, 174, 96))
    pdf.add_image_b64(graficos["diversidad"], w=170)

pdf.section_title("TEMAS VIRALES", color=(231, 76, 60))
if not df_viral.empty and "keyword" in df_viral.columns:
    top5 = df_viral.nlargest(5, "viral_score") if "viral_score" in df_viral.columns else df_viral.head(5)
    for _, row in top5.iterrows():
        kw = str(row.get("keyword",""))
        sc = row.get("viral_score", 0)
        rt = row.get("ratio", 0)
        src = str(row.get("sources",""))[:60]
        pdf.body_text(strip_emoji(f"[{sc:.0f}] x{rt:.1f} '{kw}' — {src}"))
else:
    pdf.body_text("Sin temas virales detectados.")

# ── Agenda-Setting ──
pdf.section_title("AGENDA-SETTING", color=(52, 73, 94))
if not df_agenda.empty and "source" in df_agenda.columns:
    marcadores = df_agenda[df_agenda["role"]=="Marcador de agenda"] if "role" in df_agenda.columns else df_agenda.head(5)
    pdf.body_text(f"Marcadores de agenda: {len(marcadores)}")
    top5 = marcadores.nlargest(5, "agenda_score") if "agenda_score" in marcadores.columns else marcadores.head(5)
    for _, row in top5.iterrows():
        pdf.body_text(strip_emoji(f"  {row.get('source','')} — {row.get('agenda_score',0):.1f}%"))

# Guardar PDF
try:
    pdf.output(PDF_OUT)
    print(f"[BRIEFING v2] ✅ PDF generado: {PDF_OUT}")
    # Copiar a histórico
    import shutil
    shutil.copy(PDF_OUT, os.path.join(HIST_DIR, f"briefing_{hoy}_{now.strftime('%H%M')}.pdf"))
except Exception as e:
    import traceback
    print(f"[BRIEFING v2] ❌ Error PDF: {e}")
    traceback.print_exc()
    PDF_OUT = None

# ══════════════════════════════════════════════════════════════════
# 5. GENERAR EMAIL HTML
# ══════════════════════════════════════════════════════════════════
print("[BRIEFING v2] Generando email HTML...")

def make_kpi_card(label, value, delta="", color="#2c3e50"):
    d = f'<div style="font-size:11px;color:{"#27ae60" if "▲" in delta else "#e74c3c" if "▼" in delta else "#888"}">{delta}</div>' if delta else ""
    return f"""
    <td style="padding:8px;text-align:center;background:#f8f9fa;border-radius:6px;border:1px solid #e9ecef;width:22%">
      <div style="font-size:22px;font-weight:bold;color:{color}">{value}</div>
      <div style="font-size:11px;color:#666;margin-top:2px">{label}</div>
      {d}
    </td>"""

riesgo_color = "#e74c3c" if score_riesgo >= 60 else ("#f39c12" if score_riesgo >= 30 else "#27ae60")

html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;margin:0;padding:20px}}
  .container{{max-width:700px;margin:0 auto;background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 20px rgba(0,0,0,0.1)}}
  .header{{background:linear-gradient(135deg,#2c3e50,#3498db);color:white;padding:25px;text-align:center}}
  .header h1{{margin:0;font-size:20px;letter-spacing:1px}}
  .header p{{margin:5px 0 0;opacity:0.8;font-size:12px}}
  .section{{padding:15px 20px;border-bottom:1px solid #f0f0f0}}
  .section h2{{margin:0 0 10px;font-size:14px;color:#2c3e50;border-left:4px solid #3498db;padding-left:8px}}
  .alert-high{{background:#fff5f5;border-left:4px solid #e74c3c;padding:8px 12px;margin:5px 0;border-radius:0 4px 4px 0;font-size:12px}}
  .alert-med{{background:#fffbf0;border-left:4px solid #f39c12;padding:8px 12px;margin:5px 0;border-radius:0 4px 4px 0;font-size:12px}}
  .alert-ok{{background:#f0fff4;border-left:4px solid #27ae60;padding:8px 12px;margin:5px 0;border-radius:0 4px 4px 0;font-size:12px}}
  table.kpis{{width:100%;border-collapse:separate;border-spacing:6px}}
  .persona-row{{display:flex;align-items:center;padding:4px 0;border-bottom:1px solid #f5f5f5;font-size:12px}}
  .bar-pos{{display:inline-block;background:#27ae60;height:6px;border-radius:3px;vertical-align:middle}}
  .bar-neg{{display:inline-block;background:#e74c3c;height:6px;border-radius:3px;vertical-align:middle}}
  .footer{{background:#2c3e50;color:#aaa;padding:12px;text-align:center;font-size:11px}}
  .tag{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;margin:2px}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>🇪🇸 CENTRO DE MANDO NARRATIVO ESPAÑA</h1>
  <p>Briefing Diario — {today_str} — {now_str}</p>
</div>

<div class="section">
  <table class="kpis">
    <tr>
      {make_kpi_card("Noticias 24h", n_news_hoy, _delta_txt(n_news_hoy, n_news_ay), "#3498db")}
      {make_kpi_card("Fuentes activas", n_fuentes, "", "#2ecc71")}
      {make_kpi_card("Riesgo informativo", f"{score_riesgo}/100", "", riesgo_color)}
      {make_kpi_card("Calidad pipeline", f"{audit_score}/100", "", "#9b59b6")}
    </tr>
  </table>
</div>

<div class="section">
  <h2>🤖 Resumen Ejecutivo (IA)</h2>
  <p style="font-size:13px;line-height:1.6;color:#333;background:#f8f9fa;padding:12px;border-radius:6px">{resumen_ia}</p>
</div>

<div class="section">
  <h2>🔴 Narrativas Coordinadas — {n_coord} eventos {_delta_txt(n_coord, n_coord_ay) or ''}</h2>
"""

if not df_coord.empty and "coord_score" in df_coord.columns:
    top5 = df_coord.nlargest(5, "coord_score")
    for _, row in top5.iterrows():
        sc  = row.get("coord_score", 0)
        ns  = row.get("n_sources", 0)
        rep = str(row.get("representative",""))[:80]
        cls = "alert-high" if sc >= 70 else "alert-med"
        html += f'<div class="{cls}"><strong>[{sc:.0f}] {ns:.0f} fuentes</strong> — {rep}</div>\n'
else:
    html += '<div class="alert-ok">Sin narrativas coordinadas detectadas.</div>\n'

html += f"""
</div>

<div class="section">
  <h2>⚠️ Desinformación — {n_disinfo} alertas</h2>
"""

if not df_disinfo.empty and "risk_score" in df_disinfo.columns:
    top5 = df_disinfo.nlargest(5, "risk_score")
    for _, row in top5.iterrows():
        sc    = row.get("risk_score", 0)
        src   = str(row.get("news_source",""))
        title = str(row.get("news_title",""))[:70]
        bulo  = str(row.get("bulo_title",""))[:60]
        html += f'<div class="alert-high"><strong>[{sc:.0f}] {src}</strong>: {title}<br><small style="color:#888">Bulo: {bulo}</small></div>\n'
else:
    html += '<div class="alert-ok">Sin alertas de desinformación detectadas.</div>\n'

html += f"""
</div>

<div class="section">
  <h2>🔥 Temas Virales — {n_viral}</h2>
"""

if not df_viral.empty and "keyword" in df_viral.columns:
    top5 = df_viral.nlargest(5, "viral_score") if "viral_score" in df_viral.columns else df_viral.head(5)
    for _, row in top5.iterrows():
        kw = str(row.get("keyword",""))
        sc = row.get("viral_score",0)
        rt = row.get("ratio",0)
        html += f'<span class="tag" style="background:#fff3cd;border:1px solid #ffc107">🔥 <strong>{kw}</strong> x{rt:.1f} [{sc:.0f}]</span>\n'
else:
    html += "<p style='font-size:12px;color:#888'>Sin temas virales detectados.</p>\n"

html += f"""
</div>

<div class="section">
  <h2>👤 Personajes Políticos</h2>
  <table style="width:100%;font-size:12px;border-collapse:collapse">
    <tr style="background:#f8f9fa;font-weight:bold">
      <td style="padding:5px">Personaje</td>
      <td style="padding:5px;text-align:right">Menciones</td>
      <td style="padding:5px;text-align:center;width:120px">Sentimiento</td>
    </tr>
"""

if not df_personas.empty and "persona" in df_personas.columns:
    top8 = df_personas.nlargest(8, "mentions")
    for _, row in top8.iterrows():
        p = str(row.get("persona",""))
        m = int(row.get("mentions",0))
        s = float(row.get("sentiment_score",0))
        icon = "🟢" if s > 0.05 else ("🔴" if s < -0.05 else "⚪")
        bar_w = min(80, int(abs(s)*400))
        bar_col = "#27ae60" if s > 0 else "#e74c3c"
        html += f"""<tr style="border-bottom:1px solid #f5f5f5">
          <td style="padding:4px 5px">{icon} {p}</td>
          <td style="padding:4px 5px;text-align:right">{m:,}</td>
          <td style="padding:4px 5px;text-align:center">
            <span style="display:inline-block;background:{bar_col};width:{bar_w}px;height:6px;border-radius:3px;vertical-align:middle"></span>
            <span style="font-size:10px;color:#666"> {s:+.2f}</span>
          </td>
        </tr>\n"""

html += f"""
  </table>
</div>

<div class="section">
  <h2>📊 Sentimiento NLP</h2>
"""

if not df_sentiment.empty and "sentiment" in df_sentiment.columns:
    total_s = df_sentiment["count"].sum() if "count" in df_sentiment.columns else 1
    for _, row in df_sentiment.groupby("sentiment")["count"].sum().reset_index().iterrows():
        s   = str(row["sentiment"])
        cnt = int(row["count"])
        pct = cnt / total_s * 100 if total_s > 0 else 0
        col = "#27ae60" if s=="positivo" else ("#e74c3c" if s=="negativo" else "#95a5a6")
        html += f"""<div style="margin:4px 0;font-size:12px">
          <span style="display:inline-block;width:70px;color:{col};font-weight:bold">{s}</span>
          <span style="display:inline-block;background:{col};width:{int(pct*2)}px;height:12px;border-radius:3px;vertical-align:middle;opacity:0.8"></span>
          <span style="margin-left:6px;color:#666">{cnt:,} ({pct:.1f}%)</span>
        </div>\n"""

html += f"""
</div>

<div class="section">
  <h2>🗺️ Geografía — Top CCAA</h2>
"""

if not df_geo.empty and "ccaa" in df_geo.columns:
    top8 = df_geo[df_geo["mentions"]>0].nlargest(8, "mentions")
    max_m = top8["mentions"].max() if len(top8) > 0 else 1
    for _, row in top8.iterrows():
        ccaa = str(row["ccaa"])
        m    = int(row["mentions"])
        w    = int(m / max_m * 150)
        html += f"""<div style="margin:3px 0;font-size:12px">
          <span style="display:inline-block;width:160px">{ccaa}</span>
          <span style="display:inline-block;background:#3498db;width:{w}px;height:10px;border-radius:3px;vertical-align:middle;opacity:0.7"></span>
          <span style="margin-left:6px;color:#666">{m:,}</span>
        </div>\n"""

html += f"""
</div>

<div class="footer">
  narrative-radar © M.Castillo | mybloggingnotes@gmail.com | Odroid-C2 | {now_str}<br>
  <a href="https://fake-news-narrative.streamlit.app/" style="color:#3498db">🔗 Ver dashboard completo</a>
</div>

</div>
</body>
</html>"""

# ══════════════════════════════════════════════════════════════════
# 6. ENVIAR EMAIL
# ══════════════════════════════════════════════════════════════════
print("[BRIEFING v2] Enviando email...")

try:
    with open(EMAIL_CFG) as f:
        ecfg = yaml.safe_load(f)

    msg = MIMEMultipart("mixed")
    turno = "matutino" if now.hour < 12 else "vespertino"
    msg["Subject"] = f"🇪🇸 Briefing {turno} — {today_str} | Riesgo: {nivel_riesgo} | {n_coord} narrativas coordinadas"
    msg["From"]    = ecfg["from"]
    msg["To"]      = ecfg["to"]

    # Parte HTML
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html, "html", "utf-8"))
    msg.attach(alt)

    # Adjuntar PDF
    if PDF_OUT and os.path.exists(PDF_OUT):
        with open(PDF_OUT, "rb") as f:
            pdf_data = f.read()
        att = MIMEApplication(pdf_data, _subtype="pdf")
        att.add_header("Content-Disposition", "attachment",
                       filename=f"briefing_{hoy}.pdf")
        msg.attach(att)
        print(f"[BRIEFING v2] PDF adjuntado ({len(pdf_data)//1024}KB)")

    with smtplib.SMTP_SSL(ecfg["smtp_host"], 465) as s:
        s.login(ecfg["user"], ecfg["password"])
        s.send_message(msg)

    print(f"[BRIEFING v2] ✅ Email enviado a {ecfg['to']}")

except Exception as e:
    print(f"[BRIEFING v2] ❌ Error email: {e}")
    import traceback; traceback.print_exc()

print(f"[BRIEFING v2] 🎯 Briefing completado — {now_str}")
