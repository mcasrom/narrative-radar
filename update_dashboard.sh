#!/bin/bash
# -*- coding: utf-8 -*-

# ========================================================
# Update Dashboard Pipeline - Odroid C2
# Recoge noticias reales, detecta narrativas, emociones,
# polarización y genera todos los CSV para el dashboard.
# ========================================================

echo "[INFO] Iniciando pipeline de noticias reales..."

# 1️⃣ Recolectar noticias desde RSS
echo "[INFO] Ejecutando collect_rss.py..."
python3 scripts/collect_rss.py || { echo "ERROR: collect_rss.py falló"; exit 1; }

# 2️⃣ Detectar narrativas y generar análisis
echo "[INFO] Ejecutando detect_narratives.py..."
python3 scripts/detect_narratives.py || { echo "ERROR: detect_narratives.py falló"; exit 1; }

# 3️⃣ Mensaje de finalización
echo "[INFO] Pipeline completado. Todos los CSV están listos en data/processed/"

# 4️⃣ Opcional: lanzar dashboard
# echo "[INFO] Abriendo dashboard..."
# streamlit run dashboard/dashboard_central.py
