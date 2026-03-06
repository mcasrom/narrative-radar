#!/bin/bash
# run_all_real_data.sh
# Pipeline completo para generar y preparar CSV para el dashboard con datos reales

echo "🔹 Ejecutando pipeline de recolección y análisis de datos reales..."
python3 scripts/run_all.py

echo "🔹 Preparando CSV para dashboard..."
python3 preprocess_csvs.py

echo "✅ Todo listo. Abre dashboard con: streamlit run dashboard/dashboard_central_final.py"
