#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# generate_user_guide_pdf.py
# Genera PDF completo de guía de uso del Centro de Mando Narrativo España 🇪🇸

import os
from fpdf import FPDF

def generate():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Fuente TTF válida (asegúrate de que esté en el mismo directorio)
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path)
    pdf.set_font("DejaVu", "", 12)
    
    pdf.add_page()
    
    # Título
    pdf.set_font("DejaVu", "", 16)
    pdf.cell(0, 10, "Centro de Mando Narrativo España 🇪🇸", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 6,
        "Autor: M. Castillo\n"
        "Contacto: mybloggingnotes@gmail.com\n"
        "Copyright © 2026 M.Castillo. Todos los derechos reservados.\n\n"
        "Este documento describe cómo usar el proyecto de Centro de Mando Narrativo España. "
        "Los datos representan aproximaciones basadas en análisis de fuentes de noticias, "
        "indicadores emocionales y de polarización, y se ofrecen con el mejor intento de mostrar "
        "la narrativa y tendencias actuales."
    )
    
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(0, 8, "Contenido de la Guía", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 6,
        "- Radar Narrativo: Visualiza clusters de noticias agrupadas por temática.\n"
        "- Radar Emocional: Distribución de emociones en las noticias.\n"
        "- Polarización: Índice de polarización por fecha.\n"
        "- Red de Actores: Conexiones entre fuentes de noticias y actores.\n"
        "- Propagación: Cómo se difunden las noticias en el tiempo.\n"
        "- Tendencias: Palabras clave más frecuentes.\n"
        "- Cobertura Gobierno: Alineamiento mediático hacia el gobierno.\n"
        "- Análisis Masivos: Intensidad mediática por fuente.\n"
    )
    
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(0, 8, "Interpretación de los Gráficos", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 6,
        "Cada tab del dashboard representa indicadores clave:\n\n"
        "1. Radar Narrativo: Barras de clusters, muestra cuántas noticias se agrupan por temática.\n"
        "2. Radar Emocional: Barras por emoción, permite ver la tendencia emocional de la cobertura.\n"
        "3. Polarización: Barras por fecha, permite observar cómo cambia la polarización en el tiempo.\n"
        "4. Red de Actores: Gráfico de dispersión con tamaño según peso de la conexión; identifica actores principales.\n"
        "5. Propagación: Líneas de propagación; analiza velocidad y alcance de noticias.\n"
        "6. Tendencias: Barras por keywords; detecta temas emergentes.\n"
        "7. Cobertura Gobierno: Barras por fuente y alineamiento; mide sesgo o polaridad mediática.\n"
        "8. Análisis Masivos: Líneas por fuente con intensidad; permite comparar la influencia de medios.\n\n"
        "Todos los valores son índices calculados automáticamente por los scripts de pipeline."
    )
    
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(0, 8, "Notas y Caveats", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 6,
        "- Los datos se obtienen de RSS y fuentes públicas, representan aproximaciones.\n"
        "- Algoritmos: los clusters se generan automáticamente según palabras clave; los índices (polarización, emociones, propagación) son métricas derivadas de conteos y análisis de texto.\n"
        "- Este documento no modifica los datos ni el dashboard.\n"
        "- Para análisis avanzados, los CSV se encuentran en data/processed/ y pueden abrirse externamente.\n"
        "- Las visualizaciones son interactivas en el dashboard, aquí solo se documenta su significado.\n"
    )
    
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 14)
    pdf.cell(0, 8, "Cómo usar el proyecto", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 6,
        "1. Ejecuta los scripts del pipeline para actualizar datos.\n"
        "2. Abre el dashboard central con Streamlit:\n"
        "   $ streamlit run dashboard/dashboard_central_final.py\n"
        "3. Explora los tabs interactivos.\n"
        "4. Filtra, exporta o analiza datos según necesidad.\n"
        "5. Consulta este PDF para entender métricas, índices y algoritmos."
    )
    
    # Guardar PDF
    output_dir = os.path.join(os.path.dirname(__file__), "../data/processed")
    os.makedirs(output_dir, exist_ok=True)
    output_pdf = os.path.join(output_dir, "Centro_Mando_Narrativo_Guide.pdf")
    pdf.output(output_pdf)
    print(f"✅ PDF generado: {output_pdf}")

if __name__ == "__main__":
    generate()
