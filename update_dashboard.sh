#!/bin/bash
# ------------------------------------------------------------------
# update_dashboard.sh
# Pipeline completo para el dashboard "Narrative Radar"
# Ejecuta recolección, análisis, PDF, y logrotate
# Autor: M. Castillo <mybloggingnotes@gmail.com>
# ------------------------------------------------------------------

# Variables
BASE_DIR="/home/dietpi/narrative-radar"
LOG_FILE="$BASE_DIR/pipeline.log"
LOGROTATE_CONF="$BASE_DIR/logrotate_pipeline.conf"
LOGROTATE_STATE="$BASE_DIR/logrotate_pipeline.status"
VENV_DIR="$BASE_DIR/env"

# ------------------------------------------------------------------
# Función para imprimir timestamp
# ------------------------------------------------------------------
timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

echo "[$(timestamp)] 🔹 Inicio pipeline Narrative Radar" >> "$LOG_FILE"

# ------------------------------------------------------------------
# Activar entorno virtual
# ------------------------------------------------------------------
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "[$(timestamp)] ✅ Entorno virtual activado" >> "$LOG_FILE"
else
    echo "[$(timestamp)] ⚠️ Entorno virtual no encontrado: $VENV_DIR" >> "$LOG_FILE"
    exit 1
fi


# ------------------------------------------------------------------
# Ejecutar pipeline de Python
# ------------------------------------------------------------------
echo "[$(timestamp)] 🔹 Ejecutando pipeline de recolección y análisis" >> "$LOG_FILE"

# Entramos en scripts para que el "../data" de Python apunte al sitio correcto
cd "$BASE_DIR/scripts"

python3 run_all.py >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(timestamp)] ✅ Pipeline ejecutado correctamente" >> "$LOG_FILE"
else
    echo "[$(timestamp)] ❌ Error en pipeline" >> "$LOG_FILE"
fi

# Volvemos a la base para el resto del script (PDF y logs)
cd "$BASE_DIR"

# ------------------------------------------------------------------
# Generar PDF guía del dashboard
# ------------------------------------------------------------------
echo "[$(timestamp)] 🔹 Generando PDF guía" >> "$LOG_FILE"

# Pasamos el timestamp de Bash a una variable para Python
CURRENT_TIME=$(timestamp)

python3 - <<END >> "$LOG_FILE" 2>&1
import os
import sys
from fpdf import FPDF

base_dir = "$BASE_DIR"
output_pdf = os.path.join(base_dir, "data/processed/guia_dashboard.pdf")
font_path = os.path.join(base_dir, "dashboard/DejaVuSans.ttf")
fecha_ingesta = "$CURRENT_TIME"

try:
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"No se encuentra la fuente en: {font_path}")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)
    
    texto = f"""
Centro de Mando Narrativo España

Autor: M. Castillo <mybloggingnotes@gmail.com>
Fecha de ingesta: {fecha_ingesta}

Este dashboard analiza la narrativa mediática usando fuentes RSS.
Indicadores incluidos: Radar Narrativo, Radar Emocional, Polarización, Red de Actores, 
Propagación, Tendencias, Cobertura del Gobierno, Análisis Masivo de Medios.

Los CSV se almacenan en: data/processed/
"""
    pdf.multi_cell(0, 10, texto)
    pdf.output(output_pdf)
    print("PDF generado correctamente por Python.")
except Exception as e:
    print(f"ERROR en generación de PDF: {str(e)}")
    sys.exit(1)
END

# Ahora el log dirá la verdad según el exit code de Python
if [ $? -eq 0 ]; then
    echo "[$(timestamp)] ✅ PDF guía generado en data/processed/guia_dashboard.pdf" >> "$LOG_FILE"
else
    echo "[$(timestamp)] ❌ Falló la creación del PDF guía" >> "$LOG_FILE"
fi

# ------------------------------------------------------------------
# Rotar log automáticamente
# ------------------------------------------------------------------
echo "[$(timestamp)] 🔹 Rotando logs" >> "$LOG_FILE"
/usr/sbin/logrotate --state "$LOGROTATE_STATE" "$LOGROTATE_CONF"
echo "[$(timestamp)] ✅ Logs rotados correctamente" >> "$LOG_FILE"

echo "[$(timestamp)] 🎯 Pipeline completo" >> "$LOG_FILE"

# ------------------------------------------------------------------
# Sincronización automática con GitHub (Para Streamlit Cloud)
# ------------------------------------------------------------------
echo "[$(timestamp)] 🔹 Sincronizando con GitHub..." >> "$LOG_FILE"
cd "$BASE_DIR"
git add data/processed/*.csv
git commit -m "Auto-update: Datos frescos $(date +'%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
git push origin main >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(timestamp)] ✅ GitHub actualizado" >> "$LOG_FILE"
else
    echo "[$(timestamp)] ⚠️ Error en GitHub push (posiblemente sin cambios)" >> "$LOG_FILE"
fi
