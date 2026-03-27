#!/bin/bash
# ================================================================
# update_dashboard.sh - Versión limpia y robusta (25-mar-2026)
# ================================================================

BASE_DIR="/home/dietpi/narrative-radar"
LOG_FILE="$BASE_DIR/pipeline_$(date +%Y%m%d).log"
VENV_DIR="$BASE_DIR/env"

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }

echo "[$timestamp] 🔹 === INICIO PIPELINE NARRATIVE RADAR ===" >> "$LOG_FILE"

# Activar venv correctamente
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "[$timestamp] ✅ Entorno virtual activado" >> "$LOG_FILE"
else
    echo "[$timestamp] ❌ Entorno virtual no encontrado" >> "$LOG_FILE"
    exit 1
fi

cd "$BASE_DIR"

echo "[$timestamp] 🔹 Recolectando noticias RSS..." >> "$LOG_FILE"
python scripts/collect_rss.py >> "$LOG_FILE" 2>&1

# Pipeline mínimo (evitamos scripts que se cuelgan fácilmente)
echo "[$timestamp] 🔹 Ejecutando pipeline mínimo..." >> "$LOG_FILE"

for script in \
    detect_emotions.py \
    detect_polarization.py \
    trends_analysis.py \
    government_coverage.py \
    keywords_analysis.py \
    generate_guide_pdf.py \
    detect_disinfo.py \
    detect_hate.py \
    detect_ideology.py; do

    echo "[$timestamp] → Ejecutando $script ..." >> "$LOG_FILE"
    timeout 180s python "scripts/$script" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$timestamp] ✅ $script completado" >> "$LOG_FILE"
    else
        echo "[$timestamp] ⚠️ $script finalizó con error o timeout" >> "$LOG_FILE"
    fi
done

# Scripts opcionales más pesados (pueden fallar sin romper todo)
echo "[$timestamp] 🔹 Ejecutando scripts pesados (con timeout)..." >> "$LOG_FILE"
for script in purge_history.py personas_tracking.py detect_coordination.py agenda_setting.py build_network.py propagation_analysis.py; do
    echo "[$timestamp] → Ejecutando $script ..." >> "$LOG_FILE"
    timeout 120s python "scripts/$script" >> "$LOG_FILE" 2>&1 || echo "[$timestamp] ⚠️ $script timeout o error" >> "$LOG_FILE"
done

# Rotar logs
echo "[$timestamp] 🔹 Rotando logs..." >> "$LOG_FILE"
/usr/sbin/logrotate --state "$BASE_DIR/logrotate_pipeline.status" "$BASE_DIR/logrotate_pipeline.conf" >> "$LOG_FILE" 2>&1

# Git push solo si hay cambios reales
echo "[$timestamp] 🔹 Sincronizando con GitHub..." >> "$LOG_FILE"
cd "$BASE_DIR"
git add data/processed/ news.db 2>/dev/null || true

if git diff --cached --quiet; then
    echo "[$timestamp] ⚠️ No hay cambios nuevos para subir" >> "$LOG_FILE"
else
    git commit -m "Auto-update: Datos frescos $(date +'%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
    git push origin main >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$timestamp] ✅ GitHub actualizado correctamente" >> "$LOG_FILE"
    else
        echo "[$timestamp] ❌ Error en git push" >> "$LOG_FILE"
    fi
fi

echo "[$timestamp] 🎯 === PIPELINE COMPLETO FINALIZADO ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
