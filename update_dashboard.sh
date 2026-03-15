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
echo "[$(timestamp)] 🔹 PDF ya generado por generate_guide_pdf.py en pipeline" >> "$LOG_FILE"

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
cd /home/dietpi/narrative-radar && source env/bin/activate && python3 scripts/detect_disinfo.py >> /home/dietpi/narrative-radar/pipeline.log 2>&1
cd /home/dietpi/narrative-radar && source env/bin/activate && python3 scripts/detect_hate.py >> /home/dietpi/narrative-radar/pipeline.log 2>&1
cd /home/dietpi/narrative-radar && source env/bin/activate && python3 scripts/generate_metadata.py >> /home/dietpi/narrative-radar/pipeline.log 2>&1
cd /home/dietpi/narrative-radar && git add data/processed/metadata.json && git commit -m "auto: metadata 2026-03-14 11:59" && git push >> /home/dietpi/narrative-radar/pipeline.log 2>&1
cd /home/dietpi/narrative-radar && source env/bin/activate && python3 scripts/detect_ideology.py >> /home/dietpi/narrative-radar/pipeline.log 2>&1
