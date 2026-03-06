#!/bin/bash
# run_streamlit.sh
# Despliega dashboard 24/7 en Odroid

# Ir al directorio del dashboard
cd "$(dirname "$0")/dashboard"

# Activar entorno virtual
source ../env/bin/activate

# Ejecutar Streamlit en segundo plano, puerto 8501
streamlit run dashboard_central_final.py --server.port 8501 --server.address 0.0.0.0 >> ../pipeline.log 2>&1 &
