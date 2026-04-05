#!/bin/bash
# ================================================================
# update_dashboard.sh — narrative-radar (revisado 2026-04-05)
# Fixes: $timestamp → $(timestamp), prioridades scripts,
#        narrativas en bloque crítico, PDF fuera del crítico
# ================================================================

BASE_DIR="/home/dietpi/narrative-radar"
LOG_FILE="$BASE_DIR/logs/pipeline_$(date +%Y%m%d).log"
VENV_DIR="$BASE_DIR/env"
LOCK_FILE="/tmp/update_dashboard.lock"

# ── Crear directorio de logs si no existe ────────────────────
mkdir -p "$BASE_DIR/logs"

# ── Función timestamp (llamar SIEMPRE como $(timestamp)) ─────
timestamp() { date +"%Y-%m-%d %H:%M:%S"; }

# ── Trap: liberar lock al salir por cualquier motivo ─────────
trap 'rm -f "$LOCK_FILE"; echo "[$(timestamp)] TRAP: lock liberado" >> "$LOG_FILE"' EXIT INT TERM

echo "[$(timestamp)] === INICIO PIPELINE NARRATIVE RADAR ===" >> "$LOG_FILE"

# ── Activar venv ─────────────────────────────────────────────
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "[$(timestamp)] Entorno virtual activado" >> "$LOG_FILE"
else
    echo "[$(timestamp)] ERROR: Entorno virtual no encontrado en $VENV_DIR" >> "$LOG_FILE"
    exit 1
fi

cd "$BASE_DIR" || exit 1

# ════════════════════════════════════════════════════════════
# BLOQUE 1 — RECOLECCIÓN (crítico, sin esto no hay datos)
# ════════════════════════════════════════════════════════════
echo "[$(timestamp)] --- BLOQUE 1: RECOLECCIÓN ---" >> "$LOG_FILE"
timeout 240s python scripts/collect_rss.py >> "$LOG_FILE" 2>&1
RC=$?
if [ $RC -ne 0 ]; then
    echo "[$(timestamp)] CRÍTICO: collect_rss.py falló (rc=$RC) — abortando pipeline" >> "$LOG_FILE"
    exit 1
fi
echo "[$(timestamp)] collect_rss.py OK" >> "$LOG_FILE"

# ════════════════════════════════════════════════════════════
# BLOQUE 2 — ANÁLISIS CRÍTICO (datos que alimentan el dashboard)
# Timeout conservador para Odroid C2 ARM
# ════════════════════════════════════════════════════════════
echo "[$(timestamp)] --- BLOQUE 2: ANÁLISIS CRÍTICO ---" >> "$LOG_FILE"

CRITICOS=(
    detect_narratives.py        # narrativas paradas — PRIORITARIO
    detect_emotions.py
    detect_polarization.py
    detect_sentiment_nlp.py     # subido desde opcionales
    detect_disinfo.py
    detect_hate.py
    detect_ideology.py
    trends_analysis.py
    keywords_analysis.py
    audit_quality.py
)

ERRORES_CRITICOS=0
for script in "${CRITICOS[@]}"; do
    echo "[$(timestamp)] → $script ..." >> "$LOG_FILE"
    timeout 200s python "scripts/$script" >> "$LOG_FILE" 2>&1
    RC=$?
    if [ $RC -eq 0 ]; then
        echo "[$(timestamp)]   ✓ $script OK" >> "$LOG_FILE"
    elif [ $RC -eq 124 ]; then
        echo "[$(timestamp)]   ⚠ $script TIMEOUT (>200s)" >> "$LOG_FILE"
        ERRORES_CRITICOS=$((ERRORES_CRITICOS + 1))
    else
        echo "[$(timestamp)]   ✗ $script ERROR (rc=$RC)" >> "$LOG_FILE"
        ERRORES_CRITICOS=$((ERRORES_CRITICOS + 1))
    fi
done

echo "[$(timestamp)] Bloque crítico: $ERRORES_CRITICOS errores" >> "$LOG_FILE"

# ════════════════════════════════════════════════════════════
# BLOQUE 3 — ANÁLISIS PESADO (opcionales, no bloquean el push)
# Solo si hay RAM disponible (>100MB libres)
# ════════════════════════════════════════════════════════════
echo "[$(timestamp)] --- BLOQUE 3: ANÁLISIS PESADO ---" >> "$LOG_FILE"

RAM_LIBRE=$(free -m | awk 'NR==2{print $7}')
echo "[$(timestamp)] RAM disponible: ${RAM_LIBRE}MB" >> "$LOG_FILE"

if [ "${RAM_LIBRE:-0}" -gt 100 ]; then
    PESADOS=(
        government_coverage.py
        personas_tracking.py
        mass_media_analysis.py
        detect_coordination.py
        agenda_setting.py
        build_network.py
        propagation_analysis.py
        geo_analysis.py
        detect_viral.py
        purge_history.py
    )
    for script in "${PESADOS[@]}"; do
        echo "[$(timestamp)] → $script ..." >> "$LOG_FILE"
        timeout 300s python "scripts/$script" >> "$LOG_FILE" 2>&1
        RC=$?
        if [ $RC -eq 0 ]; then
            echo "[$(timestamp)]   ✓ $script OK" >> "$LOG_FILE"
        elif [ $RC -eq 124 ]; then
            echo "[$(timestamp)]   ⚠ $script TIMEOUT" >> "$LOG_FILE"
        else
            echo "[$(timestamp)]   ✗ $script error (rc=$RC) — continuando" >> "$LOG_FILE"
        fi
    done
else
    echo "[$(timestamp)] RAM insuficiente (${RAM_LIBRE}MB) — bloque pesado omitido" >> "$LOG_FILE"
fi

# ════════════════════════════════════════════════════════════
# BLOQUE 4 — PDF (no crítico, solo si no hay errores críticos)
# ════════════════════════════════════════════════════════════
if [ "$ERRORES_CRITICOS" -lt 3 ]; then
    echo "[$(timestamp)] --- BLOQUE 4: GENERACIÓN PDF ---" >> "$LOG_FILE"
    timeout 120s python scripts/generate_guide_pdf.py >> "$LOG_FILE" 2>&1 \
        && echo "[$(timestamp)]   ✓ PDF OK" >> "$LOG_FILE" \
        || echo "[$(timestamp)]   ✗ PDF error — no crítico" >> "$LOG_FILE"
else
    echo "[$(timestamp)] Bloque PDF omitido ($ERRORES_CRITICOS errores críticos)" >> "$LOG_FILE"
fi

# ════════════════════════════════════════════════════════════
# BLOQUE 5 — GIT PUSH
# ════════════════════════════════════════════════════════════
echo "[$(timestamp)] --- BLOQUE 5: GIT PUSH ---" >> "$LOG_FILE"

python3 scripts/update_metadata.py >> "$LOG_FILE" 2>&1

cd "$BASE_DIR"
git add data/processed/ data/exports/ news.db 2>/dev/null || true

if git diff --cached --quiet; then
    echo "[$(timestamp)] Sin cambios nuevos para subir" >> "$LOG_FILE"
else
    COMMIT_MSG="auto: pipeline $(date +'%Y-%m-%d %H:%M') | errores=$ERRORES_CRITICOS"
    git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1
    git push origin main >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "[$(timestamp)] GitHub actualizado OK" >> "$LOG_FILE"
    else
        echo "[$(timestamp)] ERROR: git push falló" >> "$LOG_FILE"
    fi
fi

# ════════════════════════════════════════════════════════════
# BLOQUE 6 — ROTACIÓN DE LOGS (semanal, ligero)
# ════════════════════════════════════════════════════════════
DOW=$(date +%u)  # 7 = domingo
if [ "$DOW" -eq 7 ]; then
    echo "[$(timestamp)] Rotando logs antiguos..." >> "$LOG_FILE"
    find "$BASE_DIR/logs" -name "pipeline_*.log" -mtime +14 -delete
    echo "[$(timestamp)] Rotación completada" >> "$LOG_FILE"
fi

# ── Resumen final ─────────────────────────────────────────
echo "[$(timestamp)] === PIPELINE FINALIZADO | errores_críticos=$ERRORES_CRITICOS RAM_libre=${RAM_LIBRE}MB ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
