#!/usr/bin/env python3
"""
generate_guide_pdf.py — v1.3
Genera PDF completo de la guía C.M.N.E.
Archiva versiones anteriores en data/processed/guia_history/
"""
import os, sys, shutil
from fpdf import FPDF
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FONT = os.path.join(BASE, "dashboard/DejaVuSans.ttf")
FONT_BOLD = os.path.join(BASE, "dashboard/DejaVuSans-Bold.ttf")
OUTPUT = os.path.join(BASE, "data/processed/guia_dashboard.pdf")
HISTORY_DIR = os.path.join(BASE, "data/processed/guia_history")
os.makedirs(HISTORY_DIR, exist_ok=True)

now = datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M")
now_file = now.strftime("%Y%m%d_%H%M")

if os.path.exists(OUTPUT):
    shutil.copy2(OUTPUT, os.path.join(HISTORY_DIR, f"guia_{now_file}.pdf"))

class PDF(FPDF):
    def header(self):
        if not os.path.exists(FONT): return
        self.set_font("DejaVu", size=9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Centro de Mando Narrativo España  |  C.M.N.E.  |  v1.3", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"v1.3  |  Actualizado: {now_str}  |  Página {self.page_no()}", align="C")

    def h1(self, text):
        self.set_font("DejaVu", "B" if os.path.exists(FONT_BOLD) else "", 14)
        self.set_text_color(31, 78, 121)
        self.set_fill_color(235, 243, 251)
        self.cell(0, 10, text, ln=True, fill=True)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def h2(self, text):
        self.set_font("DejaVu", "", 11)
        self.set_text_color(46, 116, 181)
        self.cell(0, 8, text, ln=True)
        self.ln(1)
        self.set_text_color(0, 0, 0)

    def body(self, text):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("DejaVu", "", 10)
        self.set_x(15)
        self.multi_cell(0, 6, f"  -  {text}")

    def table_row(self, cols, widths, header=False, alt=False):
        self.set_font("DejaVu", "", 9)
        if header:
            self.set_fill_color(31, 78, 121)
            self.set_text_color(255, 255, 255)
        elif alt:
            self.set_fill_color(235, 243, 251)
            self.set_text_color(0, 0, 0)
        else:
            self.set_fill_color(255, 255, 255)
            self.set_text_color(0, 0, 0)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, str(col)[:50], border=1, fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)

pdf = PDF()
if not os.path.exists(FONT):
    print(f"ERROR: fuente no encontrada en {FONT}"); sys.exit(1)
pdf.add_font("DejaVu", "", FONT, uni=True)
if os.path.exists(FONT_BOLD):
    pdf.add_font("DejaVu", "B", FONT_BOLD, uni=True)

# ── PORTADA ──────────────────────────────────────────────────────
pdf.add_page()
pdf.set_font("DejaVu", "", 22)
pdf.set_text_color(31, 78, 121)
pdf.ln(20)
pdf.cell(0, 12, "Centro de Mando Narrativo España", ln=True, align="C")
pdf.set_font("DejaVu", "", 16)
pdf.set_text_color(192, 0, 0)
pdf.cell(0, 10, "C.M.N.E.", ln=True, align="C")
pdf.set_font("DejaVu", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 9, "Guia de Usuario  -  v1.3", ln=True, align="C")
pdf.ln(8)
pdf.set_font("DejaVu", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 7, f"Actualizado: {now_str}", ln=True, align="C")
pdf.cell(0, 7, "Autor: M. Castillo  |  mybloggingnotes@gmail.com", ln=True, align="C")
pdf.cell(0, 7, "https://github.com/mcasrom/narrative-radar", ln=True, align="C")
pdf.cell(0, 7, "Nodo: Odroid-C2  |  DietPi  |  24/7", ln=True, align="C")
pdf.set_text_color(0,0,0)

# ── SECCIÓN 1 ─────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("1. Descripcion del sistema")
pdf.body("El C.M.N.E. monitoriza en tiempo real la narrativa informativa española. Ingesta noticias de 28 fuentes RSS, detecta narrativas, emociones, polarizacion, desinformacion, narrativas coordinadas, temas virales y personajes politicos, y presenta todos los indicadores en un dashboard Streamlit de 18 tabs.")
pdf.body("Caracteristicas principales:")
for item in [
    "28 fuentes RSS activas — nacionales, regionales, internacionales y verificadoras",
    "Pipeline de 18 scripts — ejecucion automatica cada 30 minutos via cron",
    "Historico acumulativo — todos los modulos almacenan evolucion temporal",
    "Alertas email automaticas — desinformacion, coordinacion, virales, auditoria RSS",
    "Briefing diario — email consolidado a las 07:08 y 19:08",
    "Dashboard 18 tabs — analisis completo sin intervencion manual",
]:
    pdf.bullet(item)

# ── SECCIÓN 2 — TABS ──────────────────────────────────────────────
pdf.add_page()
pdf.h1("2. Tabs del dashboard (18)")
widths = [42, 88, 58]
pdf.table_row(["Tab", "Descripcion", "CSV fuente"], widths, header=True)
rows = [
    ["Radar Narrativo",   "Clusters TF-IDF + KMeans",             "narratives_summary.csv"],
    ["Radar Emocional",   "Distribucion emocional en titulares",   "emotions_summary.csv"],
    ["Polarizacion",      "Divergencia ideologica por dia",        "polarization_summary.csv"],
    ["Red de Actores",    "Co-actividad entre fuentes",            "actors_network.csv"],
    ["Propagacion",       "Spread index diario",                   "propagation_summary.csv"],
    ["Tendencias",        "Top 30 keywords TF-IDF",                "trends_summary.csv"],
    ["Cobertura Gobierno","Alineamiento politico por medio",       "government_coverage.csv"],
    ["Analisis Masivos",  "Intensidad de cobertura por fuente",    "mass_media_coverage.csv"],
    ["Sentimiento NLP",   "Lexico espanol expandido — score",      "sentiment_summary.csv"],
    ["Agenda-Setting",    "Marcadores vs seguidores de agenda",    "agenda_score.csv"],
    ["Coordinacion",      "Narrativas orquestadas — ventana 2h",  "coordination_alerts.csv"],
    ["Desinformacion",    "Cruce con bulos maldita/newtral",       "disinfo_alerts.csv"],
    ["Mapa Geografico",   "Menciones CCAA en titulares",           "geo_summary.csv"],
    ["Temas Virales",     "Keywords con explosion >200% en 2h",    "viral_topics.csv"],
    ["Personajes",        "Politicos clave — menciones+sentimiento","personas_summary.csv"],
    ["Diversidad",        "Originalidad informativa por fuente",   "diversity_index.csv"],
    ["Keywords",          "Emergentes, decayentes, evolucion",     "keywords_emerging.csv"],
    ["Historico",         "Evolucion temporal de todos modulos",   "*_history.csv"],
    ["Guia / HowTo",      "Estado del sistema y manual PDF",       "sources.yaml"],
]
for i, row in enumerate(rows):
    pdf.table_row(row, widths, alt=(i%2==0))

# ── SECCIÓN 3 — PIPELINE ──────────────────────────────────────────
pdf.add_page()
pdf.h1("3. Pipeline de datos (18 scripts)")
pdf.h2("3.1 Orden de ejecucion — run_all.py")
steps = [
    ("1",  "collect_rss.py",          "Ingesta 28 fuentes RSS → SQLite + news_summary.csv"),
    ("2",  "detect_narratives.py",    "TF-IDF + KMeans (5 clusters)"),
    ("3",  "detect_emotions.py",      "Lexico emocional 6 categorias"),
    ("4",  "detect_polarization.py",  "Divergencia progresista/conservador"),
    ("5",  "build_network.py",        "Co-actividad entre fuentes"),
    ("6",  "propagation_analysis.py", "Spread index diario"),
    ("7",  "trends_analysis.py",      "Keywords TF-IDF top 30"),
    ("8",  "government_coverage.py",  "Lexico politico — alineamiento"),
    ("9",  "keywords_analysis.py",    "Emergentes/decayentes por ciclo"),
    ("10", "generate_guide_pdf.py",   "Genera esta guia PDF"),
    ("11", "detect_disinfo.py",       "Cruza titulares con bulos maldita/newtral"),
    ("12", "detect_coordination.py",  "Narrativas orquestadas — ventana 2h"),
    ("13", "agenda_setting.py",       "Score marcadores vs seguidores de agenda"),
    ("14", "detect_sentiment_nlp.py", "Sentimiento lexico español expandido"),
    ("15", "geo_analysis.py",         "Menciones por Comunidad Autonoma"),
    ("16", "detect_viral.py",         "Keywords con explosion >200% en 2h"),
    ("17", "personas_tracking.py",    "Seguimiento politicos — menciones+sentimiento"),
    ("18", "diversity_index.py",      "Indice originalidad informativa por fuente"),
]
w2 = [10, 52, 126]
pdf.table_row(["N", "Script", "Descripcion"], w2, header=True)
for i, (n, script, desc) in enumerate(steps):
    pdf.table_row([n, script, desc], w2, alt=(i%2==0))

# ── SECCIÓN 4 — FUENTES ───────────────────────────────────────────
pdf.add_page()
pdf.h1("4. Fuentes RSS activas (28 / 28 OK)")
w3 = [48, 38, 102]
pdf.table_row(["Nombre", "Tipo", "URL"], w3, header=True)
sources = [
    ("elpais",               "Nacional",       "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"),
    ("elmundo",              "Nacional",       "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml"),
    ("abc",                  "Nacional",       "https://www.abc.es/rss/feeds/abc_EspanaEspana.xml"),
    ("lavanguardia",         "Nacional",       "https://www.lavanguardia.com/rss/home.xml"),
    ("eldiario",             "Nacional",       "https://www.eldiario.es/rss/"),
    ("elconfidencial",       "Nacional",       "https://rss.elconfidencial.com/espana/"),
    ("europapress",          "Nacional",       "https://www.europapress.es/rss/rss.aspx"),
    ("20minutos",            "Nacional",       "https://www.20minutos.es/rss/"),
    ("elespanol",            "Nacional",       "https://www.elespanol.com/rss/"),
    ("infolibre",            "Nacional",       "https://www.infolibre.es/rss"),
    ("okdiario",             "Nacional",       "https://okdiario.com/feed"),
    ("vozpopuli",            "Nacional",       "https://www.vozpopuli.com/feed"),
    ("expansion",            "Economia",       "https://e00-expansion.uecdn.es/rss/portada.xml"),
    ("cinco_dias",           "Economia",       "https://cincodias.elpais.com/rss/cincodias/"),
    ("elmundo_espana",       "Nacional",       "https://e00-elmundo.uecdn.es/elmundo/rss/espana.xml"),
    ("elmundo_internacional","Internacional",  "https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml"),
    ("maldita",              "Verificacion",   "https://maldita.es/feed/"),
    ("newtral",              "Verificacion",   "https://newtral.es/feed/"),
    ("bbc_mundo",            "Internacional",  "https://feeds.bbci.co.uk/mundo/rss.xml"),
    ("huffington_es",        "Internacional",  "https://www.huffingtonpost.es/feeds/index.xml"),
    ("france24_es",          "Internacional",  "https://www.france24.com/es/rss"),
    ("elpais_internacional", "Internacional",  "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional/portada"),
    ("google_news_es",       "Agregador",      "https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es"),
    ("google_news_politica", "Agregador",      "https://news.google.com/rss/search?q=politica+españa&hl=es"),
    ("heraldo_aragon",       "Regional",       "https://www.heraldo.es/rss/portada.xml"),
    ("levante_emv",          "Regional",       "https://www.levante-emv.com/rss/2.0/"),
    ("elcorreo",             "Regional",       "https://www.elcorreo.com/rss/2.0/"),
    ("cinco_dias_2",         "Economia",       "https://cincodias.elpais.com/seccion/mercados/"),
]
for i, (name, tipo, url) in enumerate(sources):
    pdf.set_font("DejaVu", "", 8)
    pdf.set_fill_color(235,243,251) if i%2==0 else pdf.set_fill_color(255,255,255)
    pdf.set_text_color(0,128,0)
    pdf.cell(w3[0], 6, name, border=1, fill=True)
    pdf.set_text_color(0,0,0)
    pdf.cell(w3[1], 6, tipo, border=1, fill=True)
    pdf.cell(w3[2], 6, url[:55], border=1, fill=True)
    pdf.ln()

# ── SECCIÓN 5 — CRONS ─────────────────────────────────────────────
pdf.add_page()
pdf.h1("5. Cron Jobs activos en Odroid-C2")
w4 = [48, 55, 85]
pdf.table_row(["Frecuencia", "Script", "Descripcion"], w4, header=True)
crons = [
    ("Cada 30 min (:00,:30)", "update_dashboard.sh",  "Pipeline completa 18 scripts con flock"),
    ("Cada 30 min (:05,:35)", "audit_sources.py",     "Auditoria RSS + email alertas caidas"),
    ("Diario 07:08",          "daily_briefing.py",    "Briefing manana — 10 secciones"),
    ("Diario 19:08",          "daily_briefing.py",    "Briefing tarde — 10 secciones"),
    ("Al reiniciar",          "run_streamlit.sh",     "Streamlit laptop puerto 8501"),
]
for i, row in enumerate(crons):
    pdf.table_row(list(row), w4, alt=(i%2==0))

pdf.ln(4)
pdf.h1("6. Alertas email automaticas")
pdf.body("El sistema envia emails automaticos en los siguientes eventos:")
alerts = [
    "Auditoria RSS — fuente con 0 entradas en ciclo",
    "Desinformacion — titular con similitud >= 0.40 con bulo verificado (score >= 60)",
    "Narrativas coordinadas — cluster de 3+ fuentes con score >= 50",
    "Temas virales — keyword con explosion >= 200% en 2h (score >= 60)",
    "Briefing diario — resumen consolidado 07:08 y 19:08",
]
for a in alerts:
    pdf.bullet(a)

# ── SECCIÓN 7 — HISTORICO ─────────────────────────────────────────
pdf.add_page()
pdf.h1("7. Historico acumulativo — CSVs generados")
w5 = [48, 68, 72]
pdf.table_row(["Modulo", "CSV principal", "CSV historico"], w5, header=True)
hist_rows = [
    ("Radar Narrativo",    "narratives_summary.csv",        "narratives_history.csv"),
    ("Radar Emocional",    "emotions_summary.csv",          "emotions_history.csv"),
    ("Polarizacion",       "polarization_summary.csv",      "polarization_history.csv"),
    ("Red de Actores",     "actors_network.csv",            "actors_network_history.csv"),
    ("Propagacion",        "propagation_summary.csv",       "propagation_history.csv"),
    ("Tendencias",         "trends_summary.csv",            "trends_history.csv"),
    ("Cob. Gobierno",      "government_coverage.csv",       "government_coverage_history.csv"),
    ("Analisis Masivos",   "mass_media_coverage.csv",       "mass_media_history.csv"),
    ("Sentimiento NLP",    "sentiment_summary.csv",         "sentiment_history.csv"),
    ("Agenda-Setting",     "agenda_score.csv",              "agenda_history.csv"),
    ("Coordinacion",       "coordination_alerts.csv",       "coordination_history.csv"),
    ("Desinformacion",     "disinfo_alerts.csv",            "disinfo_history.csv"),
    ("Mapa Geografico",    "geo_summary.csv",               "geo_history.csv"),
    ("Temas Virales",      "viral_topics.csv",              "viral_history.csv"),
    ("Personajes",         "personas_summary.csv",          "personas_history.csv"),
    ("Diversidad",         "diversity_index.csv",           "diversity_history.csv"),
    ("Keywords",           "keywords_emerging.csv",         "trends_history.csv"),
    ("Auditoria RSS",      "audit_sources.csv",             "audit_sources.csv"),
]
for i, row in enumerate(hist_rows):
    pdf.table_row(list(row), w5, alt=(i%2==0))

# ── SECCIÓN 8 — NOTAS ─────────────────────────────────────────────
pdf.add_page()
pdf.h1("8. Notas importantes")
for note in [
    "No modificar los CSV en data/processed/ — se sobreescriben en cada ciclo",
    "Para anadir fuentes RSS editar unicamente config/sources.yaml",
    "config/email.yaml esta en .gitignore — nunca se sube al repositorio",
    "El historico crece con cada ciclo — no borrar los *_history.csv",
    "Para diagnosticar errores revisar pipeline_YYYYMMDD.log",
    "El pipeline tarda ~45-60s en el Odroid-C2 — normal por ARM Cortex-A53",
    "Streamlit corre en el laptop — el Odroid solo ejecuta el pipeline",
    "Los CSVs se sincronizan via git — pull en laptop para datos frescos",
]:
    pdf.bullet(note)

pdf.ln(4)
pdf.h1("9. Changelog")
w6 = [20, 168]
pdf.table_row(["Version", "Cambios principales"], w6, header=True)
changelog = [
    ("v1.3", "18 tabs, 18 scripts: sentimiento NLP, agenda-setting, coordinacion, desinformacion, mapa geografico, temas virales, personajes politicos, diversidad informativa, briefing diario 07:08/19:08"),
    ("v1.2", "Tab Keywords, tab Historico visual, historico acumulativo en todos los modulos, auditoria email, 28 fuentes activas"),
    ("v1.1", "28 fuentes RSS, scripts con datos reales, graficos en todos los tabs"),
    ("v1.0", "Version inicial — 3 fuentes, scripts simulados, dashboard basico"),
]
for i, row in enumerate(changelog):
    pdf.set_font("DejaVu", "", 9)
    pdf.set_fill_color(235,243,251) if i%2==0 else pdf.set_fill_color(255,255,255)
    pdf.cell(w6[0], 8, row[0], border=1, fill=True)
    pdf.set_text_color(0,0,0)
    pdf.multi_cell(w6[1], 8, row[1], border=1)

pdf.output(OUTPUT)
print(f"[PDF] Guia v1.3 generada: {OUTPUT}")
print(f"[PDF] Archivada en: {HISTORY_DIR}/guia_{now_file}.pdf")
