#!/usr/bin/env python3
"""
generate_guide_pdf.py
Genera PDF completo de la guía C.M.N.E. con fecha de actualización.
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

# Archivar version anterior si existe
if os.path.exists(OUTPUT):
    shutil.copy2(OUTPUT, os.path.join(HISTORY_DIR, f"guia_{now_file}.pdf"))

class PDF(FPDF):
    def header(self):
        if not os.path.exists(FONT): return
        self.add_font("DejaVu", "", FONT, uni=True)
        if os.path.exists(FONT_BOLD):
            self.add_font("DejaVu", "B", FONT_BOLD, uni=True)
        self.set_font("DejaVu", size=9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Centro de Mando Narrativo España  |  C.M.N.E.", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"v1.2  |  Actualizado: {now_str}  |  Página {self.page_no()}", align="C")

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

    def table_row(self, cols, widths, header=False):
        self.set_font("DejaVu", "", 9)
        if header:
            self.set_fill_color(31, 78, 121)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(255, 255, 255)
            self.set_text_color(0, 0, 0)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, str(col)[:40], border=1, fill=header)
        self.ln()
        self.set_text_color(0, 0, 0)

pdf = PDF()
pdf.add_page()
if not os.path.exists(FONT):
    print(f"ERROR: fuente no encontrada en {FONT}"); sys.exit(1)
pdf.add_font("DejaVu", "", FONT, uni=True)
if os.path.exists(FONT_BOLD):
    pdf.add_font("DejaVu", "B", FONT_BOLD, uni=True)

# ── PORTADA ──────────────────────────────────────────────────────
pdf.set_font("DejaVu", "", 22)
pdf.set_text_color(31, 78, 121)
pdf.ln(20)
pdf.cell(0, 12, "Centro de Mando Narrativo Espana", ln=True, align="C")
pdf.set_font("DejaVu", "", 16)
pdf.set_text_color(192, 0, 0)
pdf.cell(0, 10, "C.M.N.E.", ln=True, align="C")
pdf.set_font("DejaVu", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 9, "Guia de Usuario  -  v1.2", ln=True, align="C")
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
pdf.h1("1. Descripción del sistema")
pdf.body("El C.M.N.E. monitoriza en tiempo real la narrativa informativa española. Ingesta noticias de 28 fuentes RSS, detecta narrativas, emociones, polarización y keywords emergentes, y presenta todos los indicadores en un dashboard Streamlit.")
pdf.body("Características principales:")
for item in [
    "28 fuentes RSS activas — nacionales, regionales e internacionales en español",
    "Pipeline automatizada — ejecución cada 30 minutos via cron en Odroid-C2",
    "Histórico acumulativo — todos los módulos almacenan evolución temporal",
    "Auditoría automática de fuentes con alerta por email",
    "Dashboard con 11 tabs — análisis completo sin intervención manual",
]:
    pdf.bullet(item)

pdf.ln(4)
pdf.h1("2. Tabs del dashboard (11)")
headers = ["Tab", "Descripción", "CSV fuente"]
widths = [38, 90, 60]
pdf.table_row(headers, widths, header=True)
rows = [
    ["Radar Narrativo", "Clusters TF-IDF + KMeans", "narratives_summary.csv"],
    ["Radar Emocional", "Distribución emocional en titulares", "emotions_summary.csv"],
    ["Polarización", "Divergencia ideológica por día", "polarization_summary.csv"],
    ["Red de Actores", "Co-actividad entre fuentes", "actors_network.csv"],
    ["Propagación", "Spread index diario", "propagation_summary.csv"],
    ["Tendencias", "Top 30 keywords TF-IDF", "trends_summary.csv"],
    ["Cobertura Gobierno", "Alineamiento político por medio", "government_coverage.csv"],
    ["Análisis Masivos", "Intensidad de cobertura por fuente", "mass_media_coverage.csv"],
    ["Keywords", "Emergentes, decayentes, evolución", "keywords_emerging/decaying.csv"],
    ["Histórico", "Visualización evolutiva de módulos", "*_history.csv"],
    ["Guía / HowTo", "Estado del sistema y manual", "sources.yaml"],
]
for i, row in enumerate(rows):
    if i % 2 == 0:
        pdf.set_fill_color(235, 243, 251)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_font("DejaVu", "", 9)
    for j, col in enumerate(row):
        pdf.cell(widths[j], 7, col, border=1, fill=True)
    pdf.ln()

# ── SECCIÓN 3 ─────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("3. Fuentes RSS activas (28 / 28 OK)")
headers2 = ["Nombre", "Tipo", "Estado"]
widths2 = [50, 40, 20]
# resto a URL
url_width = 188 - sum(widths2)
headers2.append("URL")
widths2.append(url_width)
pdf.table_row(headers2, widths2, header=True)
sources = [
    ("elpais", "Nacional", "OK"), ("elmundo", "Nacional", "OK"),
    ("abc", "Nacional", "OK"), ("lavanguardia", "Nacional", "OK"),
    ("eldiario", "Nacional", "OK"), ("elconfidencial", "Nacional", "OK"),
    ("europapress", "Nacional", "OK"), ("20minutos", "Nacional", "OK"),
    ("elespanol", "Nacional", "OK"), ("infolibre", "Nacional", "OK"),
    ("okdiario", "Nacional", "OK"), ("vozpopuli", "Nacional", "OK"),
    ("expansion", "Economía", "OK"), ("eleconomista", "Economía", "OK"),
    ("cinco_dias", "Economía", "OK"), ("elmundo_espana", "Nacional", "OK"),
    ("maldita", "Verificación", "OK"), ("newtral", "Verificación", "OK"),
    ("bbc_mundo", "Internacional", "OK"), ("huffington_es", "Internacional", "OK"),
    ("france24_es", "Internacional", "OK"), ("elpais_internacional", "Internacional", "OK"),
    ("elmundo_internacional", "Internacional", "OK"), ("google_news_es", "Agregador", "OK"),
    ("google_news_politica", "Agregador", "OK"), ("heraldo_aragon", "Regional", "OK"),
    ("levante_emv", "Regional", "OK"), ("elcorreo", "Regional", "OK"),
]
for i, (name, tipo, estado) in enumerate(sources):
    if i % 2 == 0:
        pdf.set_fill_color(235, 243, 251)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(0, 128, 0) if estado == "OK" else pdf.set_text_color(192, 0, 0)
    for j, col in enumerate([name, tipo, estado, ""]):
        pdf.cell(widths2[j], 6, col, border=1, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln()

# ── SECCIÓN 4 ─────────────────────────────────────────────────────
pdf.add_page()
pdf.h1("4. Pipeline de datos")
pdf.h2("4.1 Flujo de ejecución (run_all.py)")
steps = [
    "collect_rss.py — Ingesta 28 fuentes RSS → SQLite + news_summary.csv",
    "detect_narratives.py — TF-IDF + KMeans (5 clusters) → narratives_summary.csv",
    "detect_emotions.py — Léxico emocional (6 categorías) → emotions_summary.csv",
    "detect_polarization.py — Divergencia progresista/conservador → polarization_summary.csv",
    "build_network.py — Co-actividad entre fuentes → actors_network.csv",
    "propagation_analysis.py — Spread index por día → propagation_summary.csv",
    "trends_analysis.py — Keywords TF-IDF top 30 → trends_summary.csv",
    "government_coverage.py — Léxico político → government_coverage.csv",
    "keywords_analysis.py — Emergentes/decayentes → keywords_emerging/decaying.csv",
    "audit_sources.py — Auditoría RSS + email si hay caídas",
]
for i, step in enumerate(steps, 1):
    pdf.body(f"  {i}. {step}")

pdf.ln(2)
pdf.h2("4.2 Ejecución manual")
pdf.body("cd ~/narrative-radar && source env/bin/activate && python3 scripts/run_all.py")

pdf.ln(2)
pdf.h1("5. Cron Jobs activos en Odroid-C2")
headers3 = ["Frecuencia", "Script", "Descripción"]
widths3 = [50, 55, 83]
pdf.table_row(headers3, widths3, header=True)
crons = [
    ("Cada 30 min (:00,:30)", "update_dashboard.sh", "Pipeline completa con flock"),
    ("Cada 30 min (:05,:35)", "audit_sources.py", "Auditoría RSS + email alertas"),
    ("Al reiniciar", "run_streamlit.sh", "Streamlit en laptop puerto 8501"),
]
for i, row in enumerate(crons):
    if i % 2 == 0: pdf.set_fill_color(235, 243, 251)
    else: pdf.set_fill_color(255, 255, 255)
    pdf.set_font("DejaVu", "", 9)
    for j, col in enumerate(row):
        pdf.cell(widths3[j], 7, col, border=1, fill=True)
    pdf.ln()

pdf.ln(4)
pdf.h1("6. Histórico acumulativo")
pdf.body("Cada módulo genera CSV principal (último ciclo) y CSV histórico (todos los ciclos). El tab Histórico visualiza la evolución temporal.")
headers4 = ["Módulo", "CSV principal", "CSV histórico"]
widths4 = [45, 75, 68]
pdf.table_row(headers4, widths4, header=True)
hist_rows = [
    ("Radar Narrativo", "narratives_summary.csv", "narratives_history.csv"),
    ("Radar Emocional", "emotions_summary.csv", "emotions_history.csv"),
    ("Polarización", "polarization_summary.csv", "polarization_history.csv"),
    ("Red de Actores", "actors_network.csv", "actors_network_history.csv"),
    ("Propagación", "propagation_summary.csv", "propagation_history.csv"),
    ("Tendencias", "trends_summary.csv", "trends_history.csv"),
    ("Cobertura Gobierno", "government_coverage.csv", "government_coverage_history.csv"),
    ("Análisis Masivos", "mass_media_coverage.csv", "mass_media_history.csv"),
]
for i, row in enumerate(hist_rows):
    if i % 2 == 0: pdf.set_fill_color(235, 243, 251)
    else: pdf.set_fill_color(255, 255, 255)
    pdf.set_font("DejaVu", "", 9)
    for j, col in enumerate(row):
        pdf.cell(widths4[j], 6, col, border=1, fill=True)
    pdf.ln()

pdf.ln(4)
pdf.h1("7. Notas importantes")
for note in [
    "No modificar los CSV en data/processed/ — se sobreescriben en cada ciclo",
    "Para añadir fuentes RSS editar únicamente config/sources.yaml",
    "config/email.yaml está en .gitignore — nunca se sube al repositorio",
    "El histórico crece con cada ciclo — no borrar los *_history.csv",
    "Para diagnosticar errores revisar pipeline_YYYYMMDD.log",
]:
    pdf.bullet(note)

pdf.ln(4)
pdf.h1("8. Changelog")
headers5 = ["Versión", "Cambios principales"]
widths5 = [25, 163]
pdf.table_row(headers5, widths5, header=True)
changelog = [
    ("v1.2", "Tab Keywords, tab Histórico visual, histórico en todos los módulos, auditoría email, 28 fuentes activas"),
    ("v1.1", "28 fuentes RSS, scripts con datos reales, gráficos en todos los tabs"),
    ("v1.0", "Versión inicial — 3 fuentes, scripts simulados, dashboard básico"),
]
for i, row in enumerate(changelog):
    if i % 2 == 0: pdf.set_fill_color(235, 243, 251)
    else: pdf.set_fill_color(255, 255, 255)
    pdf.set_font("DejaVu", "", 9)
    for j, col in enumerate(row):
        pdf.cell(widths5[j], 7, col[:80], border=1, fill=True)
    pdf.ln()

pdf.output(OUTPUT)
print(f"PDF generado: {OUTPUT}")
print(f"Archivado en: {HISTORY_DIR}/guia_{now_file}.pdf")
