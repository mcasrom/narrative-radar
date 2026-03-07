#!/usr/bin/env python3
import os
import subprocess
import argparse

# -----------------------------
# Argumentos CLI
# -----------------------------
parser = argparse.ArgumentParser(description="Run all narrative radar scripts")
parser.add_argument('--seed', type=int, default=42, help="Seed para generar datos simulados")
args = parser.parse_args()

SEED = args.seed

# -----------------------------
# Función para ejecutar scripts
# -----------------------------
def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    print(f"\n--- Ejecutando {script_name} ---")
    result = subprocess.run(["python3", script_path, "--seed", str(SEED)])
    if result.returncode != 0:
        print(f"⚠️ Error ejecutando {script_name}")
    else:
        print(f"✅ {script_name} completado")

# -----------------------------
# Scripts en orden
# -----------------------------
scripts = [
    "collect_rss.py",
    "detect_narratives.py",
    "detect_emotions.py",
    "detect_polarization.py",
    "build_network.py",
    "propagation_analysis.py",
    "trends_analysis.py",
    "government_coverage.py",
    "keywords_analysis.py",
    "generate_guide_pdf.py",
    "detect_disinfo.py",
    "detect_coordination.py",
    "agenda_setting.py",
    "detect_sentiment_nlp.py"
]

# -----------------------------
# Crear carpeta processed si no existe
# -----------------------------
processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed"))
os.makedirs(processed_dir, exist_ok=True)

# -----------------------------
# Ejecutar todos los scripts
# -----------------------------
for script in scripts:
    run_script(script)

print("\n🎯 Todos los CSV generados en:", processed_dir)
