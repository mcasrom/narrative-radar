#!/usr/bin/env python3
"""
gen_guia_narrativa.py
=====================
Generador independiente de la Guía Técnica y de Usuario del
Centro de Mando Narrativo España (C.M.N.E.) v1.2

Reemplaza la función generar_pdf() del dashboard sin modificarlo.
Genera el PDF en la misma ruta que espera el dashboard:
    dashboard/guia_dashboard.pdf

Uso:
    # Desde ~/narrative-radar/dashboard/
    python3 gen_guia_narrativa.py

    # O desde cualquier directorio:
    python3 ~/narrative-radar/dashboard/gen_guia_narrativa.py

Instalación (una vez):
    ~/narrative-radar/env/bin/pip install reportlab

El dashboard lo llama así (sin modificar dashboard_central_final.py):
    Sustituye el contenido de generar_pdf() por:
        from gen_guia_narrativa import generar_pdf_completo
        return generar_pdf_completo(base_dir, current_dir, paths)

Autor: M. Castillo · mybloggingnotes@gmail.com
"""

import os
import glob
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)

# ── Paleta ─────────────────────────────────────────────────────
AZUL_DARK  = colors.HexColor("#0a1628")
AZUL       = colors.HexColor("#1a3a6e")
AZUL_MED   = colors.HexColor("#1565c0")
AZUL_CLARO = colors.HexColor("#4fc3f7")
AZUL_BG    = colors.HexColor("#e3f2fd")
NARANJA    = colors.HexColor("#e65100")
ROJO       = colors.HexColor("#b71c1c")
VERDE      = colors.HexColor("#1b5e20")
GRIS_DARK  = colors.HexColor("#263238")
GRIS_MED   = colors.HexColor("#546e7a")
GRIS_LIGHT = colors.HexColor("#eceff1")
GRIS_BG    = colors.HexColor("#f5f5f5")
BLANCO     = colors.white

W, H = A4
IW = W - 3 * cm  # ancho interior

# ── Estilos ────────────────────────────────────────────────────
def _styles():
    s = {}
    s["h1"] = ParagraphStyle("h1",
        fontName="Helvetica-Bold", fontSize=13, textColor=BLANCO,
        leading=17, spaceBefore=12, spaceAfter=6,
        backColor=AZUL, borderPad=6,
        leftIndent=-6, rightIndent=-6)
    s["h2"] = ParagraphStyle("h2",
        fontName="Helvetica-Bold", fontSize=10, textColor=AZUL,
        leading=14, spaceBefore=8, spaceAfter=4)
    s["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=9, textColor=GRIS_DARK,
        leading=13, spaceAfter=4, alignment=TA_JUSTIFY)
    s["body_en"] = ParagraphStyle("body_en",
        fontName="Helvetica-Oblique", fontSize=8.5, textColor=GRIS_MED,
        leading=12, spaceAfter=5, alignment=TA_JUSTIFY)
    s["bullet"] = ParagraphStyle("bullet",
        fontName="Helvetica", fontSize=9, textColor=GRIS_DARK,
        leading=13, leftIndent=14, spaceAfter=2)
    s["code"] = ParagraphStyle("code",
        fontName="Courier", fontSize=8, textColor=GRIS_DARK,
        leading=11, leftIndent=12, spaceAfter=1,
        backColor=GRIS_BG, borderPad=3)
    s["note"] = ParagraphStyle("note",
        fontName="Helvetica-Oblique", fontSize=8.5, textColor=NARANJA,
        leading=12, spaceAfter=4, leftIndent=8,
        backColor=colors.HexColor("#fff3e0"), borderPad=3)
    s["alert"] = ParagraphStyle("alert",
        fontName="Helvetica-Bold", fontSize=8.5, textColor=ROJO,
        leading=12, spaceAfter=4, leftIndent=8,
        backColor=colors.HexColor("#ffebee"), borderPad=3)
    s["faq_q"] = ParagraphStyle("faq_q",
        fontName="Helvetica-Bold", fontSize=9, textColor=AZUL_MED,
        leading=13, spaceBefore=8, spaceAfter=2)
    s["faq_a"] = ParagraphStyle("faq_a",
        fontName="Helvetica", fontSize=9, textColor=GRIS_DARK,
        leading=13, leftIndent=12, spaceAfter=4)
    s["footer"] = ParagraphStyle("footer",
        fontName="Helvetica", fontSize=7.5, textColor=GRIS_MED,
        leading=11, alignment=TA_CENTER)
    return s

S = _styles()

# ── Helpers ────────────────────────────────────────────────────
def sp(h=6):    return Spacer(1, h)
def hr():       return HRFlowable(width="100%", thickness=0.4,
                                  color=GRIS_LIGHT, spaceAfter=5, spaceBefore=5)
def h1(t):      return [sp(4), Paragraph(f"  {t}", S["h1"]), sp(4)]
def h2(t):      return [Paragraph(t, S["h2"])]
def body(t):    return Paragraph(t, S["body"])
def body_en(t): return Paragraph(f"<i>EN: {t}</i>", S["body_en"])
def bul(items): return [Paragraph(f"• {i}", S["bullet"]) for i in items]
def code(lines):return [Paragraph(
                    l.replace(" ", "&nbsp;").replace("<","&lt;"), S["code"])
                    for l in lines]

def tbl(data, widths=None, hbg=AZUL, hfg=BLANCO):
    if widths is None:
        widths = [IW / max(len(r) for r in data)] * len(data[0])
    pdata = []
    for ri, row in enumerate(data):
        prow = []
        for cell in row:
            if isinstance(cell, str):
                st = ParagraphStyle(f"tc{ri}",
                    fontName="Helvetica-Bold" if ri == 0 else "Helvetica",
                    fontSize=8, textColor=hfg if ri == 0 else GRIS_DARK,
                    leading=11)
                prow.append(Paragraph(cell, st))
            else:
                prow.append(cell)
        pdata.append(prow)
    t = Table(pdata, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  hbg),
        ("ROWBACKGROUND",(0,1), (-1,-1), [BLANCO, GRIS_BG]),
        ("GRID",         (0,0), (-1,-1), 0.3, GRIS_LIGHT),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ]))
    return t

# ── Header / Footer ────────────────────────────────────────────
def _on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AZUL_DARK)
    canvas.rect(0, H-1.2*cm, W, 1.2*cm, fill=1, stroke=0)
    canvas.setFillColor(BLANCO)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(1.5*cm, H-0.8*cm,
                      "C.M.N.E. · Centro de Mando Narrativo España")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(W-1.5*cm, H-0.8*cm,
                           "Guía de Usuario v1.2 · Marzo 2026")
    canvas.setFillColor(GRIS_LIGHT)
    canvas.rect(0, 0, W, 0.9*cm, fill=1, stroke=0)
    canvas.setFillColor(GRIS_MED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(1.5*cm, 0.32*cm,
                      "© 2026 M. Castillo · mybloggingnotes@gmail.com")
    canvas.drawRightString(W-1.5*cm, 0.32*cm, f"Página {doc.page}")
    canvas.restoreState()

def _on_first(canvas, doc): pass

# ── Fecha última ingestión ─────────────────────────────────────
def _ultima_ingestion(base_dir, paths=None):
    candidates = []
    if paths:
        candidates = list(paths.values())
    candidates += glob.glob(os.path.join(base_dir, "*.csv"))
    existing = [f for f in candidates if os.path.exists(f)]
    if existing:
        latest = max(existing, key=os.path.getmtime)
        mtime  = os.path.getmtime(latest)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    return "Sin datos disponibles"

# ═══════════════════════════════════════════════════════════════
# SECCIONES
# ═══════════════════════════════════════════════════════════════

def _portada(ts_gen, ts_ing):
    elems = [sp(3*cm)]
    bloque = [[Paragraph(
        "&#9632; C.M.N.E.<br/>"
        "<font size='20'><b>Centro de Mando Narrativo España</b></font><br/>"
        "<font size='11' color='#4fc3f7'>Narrative Command Center Spain &#127466;&#127480;</font><br/><br/>"
        "<font size='10'>Guía de Usuario / User Guide · v1.2</font><br/>"
        "<font size='9' color='#bbdefb'>Red de Actores · Propagación · Análisis Masivos · "
        "Desinformación · Coordinación · Agenda-Setting · NLP · 28 fuentes RSS</font>",
        ParagraphStyle("ph", fontName="Helvetica-Bold", fontSize=10,
                       textColor=BLANCO, leading=20, alignment=TA_CENTER)
    )]]
    t = Table(bloque, colWidths=[IW])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), AZUL_DARK),
        ("LEFTPADDING",  (0,0),(-1,-1), 24),
        ("RIGHTPADDING", (0,0),(-1,-1), 24),
        ("TOPPADDING",   (0,0),(-1,-1), 36),
        ("BOTTOMPADDING",(0,0),(-1,-1), 36),
    ]))
    elems.append(t)
    elems.append(sp(1.5*cm))
    meta = [
        ["Autor",               "M. Castillo · mybloggingnotes@gmail.com"],
        ["Fecha de generación", ts_gen],
        ["Última ingestión",    ts_ing],
        ["Versión dashboard",   "V1.2 · dashboard_central_final.py"],
        ["Fuentes activas",     "28 fuentes RSS (config/sources.yaml)"],
        ["Módulos activos",     "16 módulos temáticos"],
        ["Datos procesados",    "data/processed/"],
    ]
    mt = Table(meta, colWidths=[3.5*cm, IW-3.5*cm])
    mt.setStyle(TableStyle([
        ("FONTNAME",     (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",     (1,0),(1,-1), "Helvetica"),
        ("FONTSIZE",     (0,0),(-1,-1), 9),
        ("TEXTCOLOR",    (0,0),(0,-1), AZUL_MED),
        ("TEXTCOLOR",    (1,0),(1,-1), GRIS_DARK),
        ("ROWBACKGROUND",(0,0),(-1,-1), [GRIS_BG, BLANCO]),
        ("GRID",         (0,0),(-1,-1), 0.3, GRIS_LIGHT),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ]))
    elems.append(mt)
    elems.append(sp(1*cm))
    elems.append(Paragraph(
        "© 2026 M. Castillo · mybloggingnotes@gmail.com · "
        "Todos los derechos reservados", S["footer"]))
    elems.append(PageBreak())
    return elems


def _indice():
    elems = []
    elems += h1("Índice / Table of Contents")
    secs = [
        ("1",  "Introducción / Introduction"),
        ("2",  "Dashboards disponibles"),
        ("3",  "Los 16 módulos del panel"),
        ("4",  "Indicadores visuales"),
        ("5",  "Fuentes RSS — 28 fuentes activas"),
        ("6",  "Metodología y estructura de datos"),
        ("7",  "Nuevos módulos v1.1 / v1.2"),
        ("8",  "Uso de los datos"),
        ("9",  "Exportar datos y generar guía"),
        ("10", "Operación y comandos"),
        ("11", "Glosario / Glossary (ES+EN)"),
        ("12", "Preguntas frecuentes / FAQ"),
        ("A",  "Anexo: Estado del sistema"),
    ]
    idx = [["#", "Sección / Section"]] + [[n, t] for n, t in secs]
    elems.append(tbl(idx, widths=[1*cm, IW-1*cm]))
    elems.append(PageBreak())
    return elems


def _intro():
    elems = []
    elems += h1("1. Introducción / Introduction")
    elems.append(body(
        "El <b>Centro de Mando Narrativo España (C.M.N.E.)</b> es una plataforma de "
        "inteligencia narrativa basada en fuentes abiertas (OSINT) que monitoriza "
        "tendencias mediáticas, estado emocional del discurso público, polarización, "
        "desinformación, coordinación de actores y cobertura política en España "
        "mediante <b>16 módulos de análisis</b> y 28 fuentes RSS activas."
    ))
    elems.append(body_en(
        "C.M.N.E. is an OSINT platform monitoring media trends, emotional state of "
        "public discourse, polarization, disinformation, actor coordination, and "
        "political coverage in Spain via 16 analysis modules and 28 active RSS sources."
    ))
    elems.append(sp(4))
    elems.append(body(
        "<b>Infraestructura:</b> feeds RSS ingestados por <code>collect_rss_real.py</code>, "
        "procesados por scripts independientes en <code>scripts/</code> y almacenados "
        "como CSVs en <code>data/processed/</code>. El dashboard Streamlit "
        "<code>dashboard_central_final.py</code> los visualiza en tiempo real."
    ))
    return elems


def _dashboards():
    elems = []
    elems += h1("2. Dashboards disponibles")
    d = [
        ["Archivo", "Descripción"],
        ["dashboard_central_final.py",
         "Dashboard principal activo — 16 módulos + guía + metadatos"],
        ["dashboard_central.py",
         "Versión anterior (mantenida como backup)"],
        ["dashboard_howto.py / howto_tab.py",
         "Tab de ayuda embebida (integrada en el principal)"],
        ["radar_narrativo.py",
         "Módulo standalone del radar narrativo"],
    ]
    elems.append(tbl(d, widths=[5*cm, IW-5*cm]))
    return elems


def _modulos():
    elems = []
    elems += h1("3. Los 16 módulos del panel")
    elems.append(body(
        "Cada módulo carga su CSV de <code>data/processed/</code>. Si el archivo "
        "no existe o está vacío, muestra un aviso sin interrumpir el resto del dashboard."
    ))
    elems.append(sp(4))
    mods = [
        ["Módulo", "CSV", "Visualización"],
        ["Radar Narrativo",    "narratives_summary.csv",    "Barras por cluster"],
        ["Radar Emocional",    "emotions_summary.csv",      "Barras por emoción"],
        ["Polarización",       "polarization_summary.csv",  "Línea temporal azul"],
        ["Red de Actores",     "actors_network.csv",        "Barras source-target-weight"],
        ["Propagación",        "propagation_summary.csv",   "Línea temporal naranja"],
        ["Tendencias",         "trends_summary.csv",        "Barras por keyword"],
        ["Cobertura Gobierno", "government_coverage.csv",   "Barras por fuente/alineamiento"],
        ["Análisis Masivos",   "mass_media_coverage.csv",   "Barras escala Reds"],
        ["Desinformación",     "disinfo_alerts.csv",        "Alertas y tabla"],
        ["Coordinación",       "coordination_alerts.csv",   "Alertas y tabla"],
        ["Agenda-Setting",     "agenda_score.csv",          "Score por tema/fuente"],
        ["Sentimiento NLP",    "sentiment_summary.csv",     "Distribución sentiment"],
        ["Mapa Geográfico",    "geo_summary.csv",           "Scatter geo / mapa"],
        ["Temas Virales",      "viral_topics.csv",          "Barras por velocidad viral"],
        ["Personajes",         "personas_summary.csv",      "Barras por persona/aparición"],
        ["Diversidad",         "diversity_index.csv",       "Índice de diversidad mediática"],
    ]
    elems.append(tbl(mods, widths=[3.5*cm, 4.8*cm, IW-8.3*cm]))
    return elems


def _indicadores():
    elems = []
    elems += h1("4. Indicadores visuales")
    tipos = [
        ["Tipo", "Módulos", "Detalle"],
        ["Barras (bar)",        "Narrativo, Emocional, Tendencias, Cobertura, Actores, Masivos, Virales, Personajes",
         "Comparación de frecuencias por categoría"],
        ["Línea azul",          "Polarización",
         "Evolución temporal del índice de polarización"],
        ["Línea naranja",       "Propagación",
         "Evolución temporal del índice de propagación"],
        ["Barras escala Reds",  "Análisis Masivos",
         "Intensidad — escala de color continua"],
        ["Alertas / tabla",     "Desinformación, Coordinación",
         "Listado de alertas con severidad y fuente"],
        ["Scatter geo",         "Mapa Geográfico",
         "Distribución geográfica de noticias (lat/lon)"],
        ["Score numérico",      "Agenda-Setting, Diversidad",
         "Índices cuantitativos normalizados 0-100"],
        ["Tabla (dataframe)",   "Todos los módulos",
         "Vista raw de registros del CSV"],
    ]
    elems.append(tbl(tipos, widths=[3*cm, 5*cm, IW-8*cm]))
    return elems


def _fuentes():
    elems = []
    elems += h1("5. Fuentes RSS — 28 fuentes activas")
    elems.append(body(
        "Gestionadas en <code>config/sources.yaml</code>. "
        "<code>collect_rss_real.py</code> las carga dinámicamente en cada ciclo — "
        "añadir o desactivar fuentes no requiere modificar código Python."
    ))
    elems.append(sp(4))
    fuentes = [
        ["Fuente", "Tipo", "Categoría"],
        ["El País",              "news",         "Nacional generalista"],
        ["El Mundo",             "news",         "Nacional generalista"],
        ["ABC",                  "news",         "Nacional conservador"],
        ["El Diario",            "news",         "Nacional progresista"],
        ["El Español",           "news",         "Nacional generalista"],
        ["El Confidencial",      "news",         "Económico/político"],
        ["Infolibre",            "news",         "Análisis político"],
        ["El Periódico",         "news",         "Cataluña/nacional"],
        ["20 Minutos",           "news",         "Nacional trending"],
        ["Europa Press",         "news",         "Tiempo real"],
        ["RTVE",                 "news",         "TV/Radio pública"],
        ["La Sexta",             "news",         "TV nacional"],
        ["Cadena SER",           "news",         "Radio nacional"],
        ["COPE",                 "news",         "Radio conservadora"],
        ["Maldita.es",           "verification", "Fact-checking nacional"],
        ["Newtral",              "verification", "Fact-checking nacional"],
        ["BBC Mundo",            "news",         "Internacional en español"],
        ["Reuters España",       "news",         "Internacional"],
        ["DW Español",           "news",         "Internacional"],
        ["France24 Español",     "news",         "Internacional"],
        ["El País Internacional","news",         "Internacional"],
        ["Google News ES",       "aggregator",   "Agregador global"],
        ["La Voz de Galicia",    "news",         "Regional — Galicia"],
        ["Heraldo de Aragón",    "news",         "Regional — Aragón"],
        ["Levante-EMV",          "news",         "Regional — C. Valenciana"],
        ["Diario Sur",           "news",         "Regional — Andalucía"],
        ["La Vanguardia",        "news",         "Nacional/Cataluña"],
        ["Público",              "news",         "Nacional progresista"],
    ]
    elems.append(tbl(fuentes, widths=[4.5*cm, 2.5*cm, IW-7*cm]))
    elems.append(sp(6))
    elems += h2("Añadir o desactivar fuentes")
    elems += code([
        "# Editar config/sources.yaml:",
        "- name: nombre_corto",
        "  url: https://ejemplo.com/rss",
        "  type: news",
        "",
        "# Desactivar: comentar o eliminar el bloque",
        "# Activo en el siguiente ciclo de collect_rss_real.py",
    ])
    return elems


def _metodologia():
    elems = []
    elems += h1("6. Metodología y estructura de datos")
    elems.append(body(
        "El sistema analiza exclusivamente fuentes abiertas (OSINT). "
        "Cada módulo tiene su propio script de procesamiento en <code>scripts/</code> "
        "y su propio CSV de salida en <code>data/processed/</code>."
    ))
    elems.append(sp(4))
    esquema = [
        ["Módulo", "Columnas clave requeridas"],
        ["Radar Narrativo",    "cluster, count"],
        ["Radar Emocional",    "emotion, count"],
        ["Polarización",       "date, polarization_index"],
        ["Red de Actores",     "source, target, weight"],
        ["Propagación",        "date, spread_index"],
        ["Tendencias",         "keyword, count"],
        ["Cobertura Gobierno", "source, alignment"],
        ["Análisis Masivos",   "source, intensity_index"],
        ["Desinformación",     "date, source, claim, severity"],
        ["Coordinación",       "date, actor_a, actor_b, score"],
        ["Agenda-Setting",     "topic, source, agenda_score"],
        ["Sentimiento NLP",    "label, count  (positive/negative/neutral)"],
        ["Mapa Geográfico",    "lat, lon, title, source"],
        ["Temas Virales",      "topic, viral_score, date"],
        ["Personajes",         "persona, count, sentiment"],
        ["Diversidad",         "source, diversity_index"],
    ]
    elems.append(tbl(esquema, widths=[4*cm, IW-4*cm]))
    elems.append(sp(6))
    elems += h2("Limitaciones")
    elems += bul([
        "El sistema <b>NO verifica</b> la veracidad de las noticias individuales",
        "Un score alto indica <b>VOLUMEN</b> de cobertura, no confirmación de hechos",
        "Si un CSV no existe, el módulo muestra aviso sin interrumpir el dashboard",
        "Algunas fuentes RSS pueden devolver 0 entradas si el feed está caído",
        "Los modelos NLP (sentimiento, narrativas) pueden tener sesgos de entrenamiento",
    ])
    return elems


def _novedades():
    elems = []
    elems += h1("7. Nuevos módulos v1.1 / v1.2")
    novedades = [
        ("Red de Actores", "actors_network.csv",
         "source, target, weight",
         "Peso de relaciones entre actores mediáticos. Identifica co-apariciones "
         "relevantes y flujos de influencia entre medios y personas."),
        ("Propagación", "propagation_summary.csv",
         "date, spread_index",
         "Evolución temporal del índice de difusión narrativa. Detecta picos de "
         "propagación y los correlaciona con eventos externos."),
        ("Análisis Masivos", "mass_media_coverage.csv",
         "source, intensity_index",
         "Intensidad comparativa de cobertura entre medios masivos mediante "
         "escala de color continua (Reds). Detecta amplificadores narrativos."),
        ("Desinformación", "disinfo_alerts.csv",
         "date, source, claim, severity",
         "Alertas de contenido potencialmente desinformativo detectado en las "
         "fuentes. Clasificado por severidad (Alta/Media/Baja)."),
        ("Coordinación", "coordination_alerts.csv",
         "date, actor_a, actor_b, score",
         "Detección de patrones de coordinación inorgánica entre actores o medios. "
         "Score de 0-1 indica probabilidad de coordinación."),
        ("Agenda-Setting", "agenda_score.csv",
         "topic, source, agenda_score",
         "Mide qué temas están siendo empujados activamente por cada fuente "
         "más allá de su cobertura proporcional."),
        ("Sentimiento NLP", "sentiment_summary.csv",
         "label, count",
         "Distribución de sentimiento (positivo/negativo/neutral) en los textos "
         "analizados mediante modelos NLP."),
        ("Mapa Geográfico", "geo_summary.csv",
         "lat, lon, title, source",
         "Distribución geográfica de las noticias analizadas sobre mapa interactivo."),
        ("Temas Virales", "viral_topics.csv",
         "topic, viral_score, date",
         "Temas con mayor velocidad de propagación en el ciclo analizado."),
        ("Personajes", "personas_summary.csv",
         "persona, count, sentiment",
         "Seguimiento de personas/actores con más apariciones y su valencia "
         "emocional asociada en el discurso mediático."),
        ("Diversidad", "diversity_index.csv",
         "source, diversity_index",
         "Índice de diversidad mediática por fuente — mide pluralidad temática."),
    ]
    for nombre, csv, cols, desc in novedades:
        elems.append(KeepTogether([
            Paragraph(f"▶ {nombre} — <code>{csv}</code>",
                ParagraphStyle("nov_t", fontName="Helvetica-Bold", fontSize=9,
                               textColor=AZUL_MED, leading=13,
                               spaceBefore=8, spaceAfter=2)),
            Paragraph(f"Columnas: <i>{cols}</i>",
                ParagraphStyle("nov_c", fontName="Helvetica-Oblique", fontSize=8,
                               textColor=GRIS_MED, leading=11, spaceAfter=2,
                               leftIndent=12)),
            Paragraph(desc,
                ParagraphStyle("nov_d", fontName="Helvetica", fontSize=9,
                               textColor=GRIS_DARK, leading=12,
                               leftIndent=12, spaceAfter=4)),
        ]))
    return elems


def _uso():
    elems = []
    elems += h1("8. Uso de los datos")
    elems += bul([
        "Seguimiento de tendencias narrativas en medios españoles a medio y largo plazo",
        "Detección temprana de escaladas emocionales o de polarización en el discurso público",
        "Identificación de patrones de desinformación y coordinación inorgánica",
        "Comparación de intensidad de cobertura entre diferentes actores y temas",
        "Análisis de agenda-setting y amplificación narrativa por medio",
        "Input para análisis de riesgo narrativo en contextos de comunicación estratégica",
    ])
    elems.append(sp(4))
    elems.append(Paragraph(
        "⚠ No recomendado para toma de decisiones operativas críticas sin verificación "
        "adicional. No usar como única fuente de inteligencia en situaciones de alta consecuencia.",
        S["alert"]
    ))
    elems.append(sp(4))
    elems.append(body(
        "Para investigación: datos en CSV adecuados para análisis estadístico, "
        "series temporales y modelos predictivos. "
        "Citar como: <i>C.M.N.E. / M. Castillo / mybloggingnotes@gmail.com</i>"
    ))
    return elems


def _exportar():
    elems = []
    elems += h1("9. Exportar datos y generar guía")
    export = [
        ["Acción", "Método", "Resultado"],
        ["Generar guía PDF",
         "python3 dashboard/gen_guia_narrativa.py",
         "dashboard/guia_dashboard.pdf (reemplaza la anterior)"],
        ["Ver última ingestión",
         "Panel inferior del dashboard",
         "Fecha real basada en mtime del CSV de Tendencias"],
        ["Exportar CSV raw",
         "Acceso al filesystem",
         "data/processed/*.csv"],
        ["Añadir fuentes RSS",
         "Editar config/sources.yaml",
         "Activo en el siguiente ciclo de collect_rss_real.py"],
        ["Historial de guías",
         "dashboard/guia_history/",
         "Versiones anteriores del PDF con timestamp"],
    ]
    elems.append(tbl(export, widths=[3.5*cm, 4.5*cm, IW-8*cm]))
    return elems


def _operacion():
    elems = []
    elems += h1("10. Operación y comandos")

    elems += h2("Lanzar el dashboard")
    elems += code([
        "cd ~/narrative-radar",
        "source env/bin/activate",
        "streamlit run dashboard/dashboard_central_final.py \\",
        "    --server.address 0.0.0.0 --server.port 8501 \\",
        "    --server.headless true",
        "",
        "# O usando el script incluido:",
        "bash run_streamlit.sh",
    ])
    elems.append(sp(6))

    elems += h2("Ejecutar ingestión completa manualmente")
    elems += code([
        "cd ~/narrative-radar && source env/bin/activate",
        "python3 scripts/collect_rss_real.py    # recoger RSS",
        "bash scripts/run_all_real_data.sh       # procesar todos los módulos",
    ])
    elems.append(sp(6))

    elems += h2("Generar guía PDF actualizada")
    elems += code([
        "cd ~/narrative-radar && source env/bin/activate",
        "python3 dashboard/gen_guia_narrativa.py",
        "# → dashboard/guia_dashboard.pdf",
    ])
    elems.append(sp(6))

    elems += h2("Cron recomendado")
    cron = [
        ["Hora", "Comando", "Acción"],
        ["0 6 * * *",
         "bash ~/narrative-radar/update_dashboard.sh",
         "Ingestión + procesado + push git"],
        ["30 6 * * *",
         "python3 dashboard/gen_guia_narrativa.py",
         "Regenerar guía con fecha real de ingestión"],
    ]
    elems.append(tbl(cron, widths=[2.5*cm, 5*cm, IW-7.5*cm]))
    elems.append(sp(6))

    elems += h2("Gestión como servicio systemd")
    elems += code([
        "sudo systemctl status narrative-radar",
        "sudo systemctl restart narrative-radar",
        "tail -f ~/narrative-radar/logs/streamlit.log",
    ])
    return elems


def _glosario():
    elems = []
    elems += h1("11. Glosario / Glossary")
    glos = [
        ["Término", "Definición ES", "EN"],
        ["OSINT",              "Inteligencia de fuentes abiertas",
         "Open Source Intelligence"],
        ["Cluster narrativo",  "Agrupación temática de narrativas similares",
         "Thematic grouping of similar narratives"],
        ["Polarización",       "Métrica de divergencia discursiva (0-100)",
         "Discursive divergence metric (0-100)"],
        ["Spread index",       "Índice de velocidad y alcance de propagación",
         "Speed and reach propagation index"],
        ["Intensity index",    "Índice de intensidad de cobertura por medio",
         "Coverage intensity index per medium"],
        ["Agenda-setting",     "Capacidad de un medio de imponer temas al debate",
         "Media power to set the public agenda"],
        ["Alineamiento",       "Grado de correspondencia con el discurso gubernamental",
         "Degree of alignment with government discourse"],
        ["Disinfo alert",      "Alerta de contenido potencialmente desinformativo",
         "Potentially disinformative content alert"],
        ["Coordinación",       "Patrón de acción concertada entre actores mediáticos",
         "Concerted action pattern among media actors"],
        ["Viral score",        "Índice de velocidad de propagación de un tema",
         "Topic propagation speed index"],
        ["Diversity index",    "Pluralidad temática de una fuente (0-1)",
         "Source thematic plurality (0-1)"],
        ["mtime",              "Fecha de modificación del archivo (sistema)",
         "File modification timestamp"],
        ["sources.yaml",       "Archivo de configuración de fuentes RSS activas",
         "Active RSS sources config file"],
        ["feedparser",         "Librería Python para parsear feeds RSS/Atom",
         "Python library for RSS/Atom parsing"],
        ["weight",             "Peso numérico de una relación entre actores (0-1)",
         "Numeric relationship weight (0-1)"],
    ]
    elems.append(tbl(glos, widths=[3*cm, 5.2*cm, IW-8.2*cm]))
    return elems


def _faq():
    elems = []
    elems += h1("12. Preguntas frecuentes / FAQ")
    faqs = [
        ("¿Con qué frecuencia se actualizan los datos?",
         "Depende del cron configurado. La fecha real aparece en el pie del dashboard "
         "basada en el mtime del trends_summary.csv."),
        ("¿Qué ocurre si un CSV no existe o está vacío?",
         "El módulo muestra aviso en amarillo y el resto del dashboard sigue funcionando."),
        ("¿Por qué algunas fuentes devuelven 0 entradas?",
         "El feed puede estar caído, la URL cambiada, o el medio bloquea scrapers. "
         "Revisa y actualiza la URL en config/sources.yaml."),
        ("¿Cómo añado una fuente RSS nueva?",
         "Edita config/sources.yaml con name, url y type. Activo en el siguiente ciclo "
         "sin modificar ningún script Python."),
        ("¿Un índice de polarización alto significa crisis política?",
         "No necesariamente — refleja VOLUMEN e INTENSIDAD de cobertura mediática sobre "
         "tensión discursiva. Verificar siempre con fuentes primarias."),
        ("¿Qué diferencia hay entre Propagación y Polarización?",
         "Polarización mide DIVERGENCIA entre posturas. "
         "Propagación mide VELOCIDAD Y ALCANCE de difusión. "
         "Pueden moverse de forma independiente."),
        ("¿Cómo interpreto una alerta de Coordinación?",
         "Un score alto indica probabilidad de acción concertada entre dos actores. "
         "No implica prueba definitiva — es una señal de investigación adicional."),
        ("¿La guía PDF se genera automáticamente?",
         "No de forma automática, pero puedes añadirla al cron tras la ingestión: "
         "python3 dashboard/gen_guia_narrativa.py"),
        ("¿Se conservan los datos históricos?",
         "Los CSVs se sobreescriben en cada ciclo salvo que run_all_real_data.sh "
         "implemente archivado histórico incremental."),
        ("¿Puedo desplegar en Streamlit Cloud?",
         "Sí. Sube el repositorio a GitHub y apunta Streamlit Cloud a "
         "dashboard/dashboard_central_final.py como archivo principal."),
    ]
    for q, a in faqs:
        elems.append(KeepTogether([
            Paragraph(f"&#9658; {q}", S["faq_q"]),
            Paragraph(a, S["faq_a"]),
        ]))
    return elems


def _anexo(ts_gen, ts_ing, base_dir):
    elems = []
    elems += h1("Anexo: Estado del sistema en el momento de generación")
    # Contar CSVs disponibles
    csvs = glob.glob(os.path.join(base_dir, "*.csv"))
    n_csvs = len(csvs)
    cap = [
        ["Parámetro", "Valor"],
        ["Fecha de generación",       ts_gen],
        ["Última ingestión detectada",ts_ing],
        ["CSVs en data/processed/",   f"{n_csvs} archivos"],
        ["Generado por",              "gen_guia_narrativa.py"],
        ["Versión",                   "v1.2 · Marzo 2026"],
        ["Autor",                     "M. Castillo · mybloggingnotes@gmail.com"],
        ["Módulos configurados",      "16 módulos temáticos"],
        ["Fuentes RSS",               "28 fuentes activas"],
    ]
    elems.append(tbl(cap, widths=[5*cm, IW-5*cm]))
    return elems


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL — llamable desde dashboard o CLI
# ═══════════════════════════════════════════════════════════════

def generar_pdf_completo(base_dir=None, current_dir=None, paths=None):
    """
    Genera la guía completa y devuelve la ruta del PDF.
    Compatible con la firma esperada por dashboard_central_final.py.

    Parámetros:
        base_dir    : ruta a data/processed/ (se autodetecta si es None)
        current_dir : ruta al directorio dashboard/ (se autodetecta si es None)
        paths       : dict de {módulo: ruta_csv} del dashboard (opcional)

    Retorna:
        str: ruta absoluta del PDF generado
    """
    if current_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir is None:
        base_dir = os.path.abspath(
            os.path.join(current_dir, "../data/processed"))

    output_pdf = os.path.join(current_dir, "guia_dashboard.pdf")
    os.makedirs(base_dir, exist_ok=True)

    ts_gen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_ing = _ultima_ingestion(base_dir, paths)

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.8*cm,  bottomMargin=1.5*cm,
        title="Guía de Usuario — C.M.N.E. v1.2",
        author="M. Castillo · mybloggingnotes@gmail.com",
        subject="Centro de Mando Narrativo España · Dashboard OSINT v1.2",
    )

    story = []
    story += _portada(ts_gen, ts_ing)
    story += _indice()
    story += _intro()
    story += _dashboards()
    story += _modulos()
    story += [PageBreak()]
    story += _indicadores()
    story += _fuentes()
    story += [PageBreak()]
    story += _metodologia()
    story += [PageBreak()]
    story += _novedades()
    story += [PageBreak()]
    story += _uso()
    story += _exportar()
    story += _operacion()
    story += [PageBreak()]
    story += _glosario()
    story += [PageBreak()]
    story += _faq()
    story += [PageBreak()]
    story += _anexo(ts_gen, ts_ing, base_dir)

    # Página final
    story.append(PageBreak())
    story.append(sp(6*cm))
    story.append(tbl([[Paragraph(
        "Centro de Mando Narrativo España · C.M.N.E.<br/>"
        "© 2026 M. Castillo · mybloggingnotes@gmail.com<br/>"
        "Todos los derechos reservados · Marzo 2026",
        ParagraphStyle("fin", fontName="Helvetica", fontSize=10,
                       textColor=BLANCO, alignment=TA_CENTER, leading=16)
    )]], widths=[IW]))

    doc.build(story, onFirstPage=_on_first, onLaterPages=_on_page)
    print(f"Guia generada: {output_pdf}  [{ts_ing}]")
    return output_pdf


# ── CLI directo ────────────────────────────────────────────────
if __name__ == "__main__":
    generar_pdf_completo()
