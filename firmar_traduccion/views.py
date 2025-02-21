import io
import os
import fitz  # PyMuPDF
import subprocess
from django.http import FileResponse
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from PIL import Image

import subprocess
import platform
from docx2pdf import convert

def convertir_docx_a_pdf(input_path, output_path):
    """Convierte un DOCX a PDF, usando la mejor opción según el SO."""
    
    sistema = platform.system()
    
    if sistema == "Windows":
        try:
            convert(input_path, output_path)  # Usa docx2pdf en Windows
        except Exception as e:
            raise RuntimeError(f"Error en conversión en Windows: {e}")
    
    else:  # Linux o macOS (Render usará Linux)
        command = ["libreoffice", "--headless", "--convert-to", "pdf", input_path]
        try:
            subprocess.run(command, check=True)
            converted_file = input_path.replace(".docx", ".pdf")
            if os.path.exists(converted_file):
                os.rename(converted_file, output_path)
        except Exception as e:
            raise RuntimeError(f"Error en conversión en Linux: {e}")



def firmar_documento(request):
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo_word = request.FILES["archivo"]
        firma_nombre = request.POST.get("firma")
        print("📄 Recibido archivo para firmar.")

        if not archivo_word.name.endswith(".docx"):
            print("❌ Error: El archivo no es un .docx")
            return render(request, "index.html", {"error": "El archivo debe ser un documento .docx"})

        ruta_word = default_storage.save("temp.docx", archivo_word)
        ruta_word_absoluta = default_storage.path(ruta_word)
        ruta_pdf = ruta_word_absoluta.replace(".docx", ".pdf")

        try:
            # Convertir a PDF
            convertir_docx_a_pdf(ruta_word_absoluta, ruta_pdf)
            print("✅ Conversión a PDF exitosa.")

            # Agregar la firma al PDF
            pdf_firmado = agregar_firma(ruta_pdf, firma_nombre)
            response = FileResponse(pdf_firmado, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="documento_firmado.pdf"'
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return render(request, "index.html", {"error": str(e)})

        finally:
            # Eliminar archivos temporales
            if os.path.exists(ruta_word_absoluta):
                os.remove(ruta_word_absoluta)
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)

        return response

    return render(request, "index.html")


def agregar_firma(ruta_pdf, firma_nombre):
    print("✍️ Agregando firma al PDF...")
    doc = fitz.open(ruta_pdf)
    firma_path = os.path.join(settings.MEDIA_ROOT, "firmas", firma_nombre)

    if not os.path.exists(firma_path):
        print(f"❌ Error: No se encontró la firma en {firma_path}")
        raise FileNotFoundError(f"La firma {firma_nombre} no existe en media/firmas/")

    with Image.open(firma_path) as img:
        firma_ancho, firma_alto = img.size

    # Ajustar tamaño de la firma dinámicamente
    factor_conversion = 0.45 # Tamaño relativo
    for page in doc:
        ancho_pagina = page.rect.width
        alto_pagina = page.rect.height

        firma_ancho_ajustado = firma_ancho * factor_conversion
        firma_alto_ajustado = firma_alto * factor_conversion

        margen_inferior = 20
        margen_derecho = 10

        rect = fitz.Rect(
            ancho_pagina - firma_ancho_ajustado - margen_derecho,
            alto_pagina - firma_alto_ajustado - margen_inferior,
            ancho_pagina - margen_derecho,
            alto_pagina - margen_inferior
        )

        page.insert_image(rect, filename=firma_path)

    pdf_output = io.BytesIO()
    doc.save(pdf_output)
    pdf_output.seek(0)
    print("✅ Firma agregada correctamente.")
    return pdf_output
