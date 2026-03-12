import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Localizar líneas 749-771 (índice 0 = línea 1)
start = None
end   = None
for i, l in enumerate(lines):
    if "def generar_pdf():" in l and start is None:
        start = i
    if start and i > start and "return output_pdf" in l:
        end = i
        break

if start is None or end is None:
    print(f"ERROR: no encontré la función (start={start}, end={end})")
    sys.exit(1)

print(f"Reemplazando líneas {start+1}–{end+1}")

nueva_funcion = """\
def generar_pdf():
    try:
        from gen_guia_narrativa import generar_pdf_completo
        return generar_pdf_completo(base_dir, current_dir, paths)
    except ImportError:
        # Fallback: generador mínimo original (fpdf)
        from fpdf import FPDF
        import os
        from datetime import datetime
        pdf = FPDF()
        pdf.add_page()
        font_path = os.path.join(current_dir, "DejaVuSans.ttf")
        if os.path.exists(font_path):
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
        else:
            pdf.set_font("Arial", size=12)
        testigo = paths["Tendencias"]
        fecha_pdf = datetime.fromtimestamp(os.path.getmtime(testigo)).strftime("%Y-%m-%d %H:%M:%S") if os.path.exists(testigo) else "N/A"
        texto = f"Centro de Mando Narrativo España\\nAutor: M. Castillo\\nFecha: {fecha_pdf}\\nCSV: data/processed/"
        pdf.multi_cell(0, 10, texto)
        output_pdf = os.path.join(base_dir, "guia_dashboard.pdf")
        pdf.output(output_pdf)
        return output_pdf
"""

new_lines = lines[:start] + [nueva_funcion] + lines[end+1:]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("OK — función reemplazada correctamente")
