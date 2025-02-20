import io
import fitz  # PyMuPDF
from django.http import FileResponse
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
import os
from docx2pdf import convert

def firmar_documento(request):
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo_word = request.FILES["archivo"]
        firma_nombre = request.POST.get("firma")

        # Validar que sea un archivo .docx
        if not archivo_word.name.endswith(".docx"):
            return render(request, "index.html", {"error": "El archivo debe ser un documento .docx"})

        # Guardar archivo temporalmente
        ruta_word = default_storage.save("temp.docx", archivo_word)
        ruta_word_absoluta = default_storage.path(ruta_word)
        ruta_pdf = ruta_word_absoluta.replace(".docx", ".pdf")

        # Convertir Word a PDF manteniendo formato
        convert(ruta_word_absoluta, ruta_pdf)

        # Agregar firma en la parte inferior derecha
        pdf_firmado = agregar_firma(ruta_pdf, firma_nombre)

        # Responder con el PDF firmado
        response = FileResponse(pdf_firmado, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="documento_firmado.pdf"'
        return response

    return render(request, "index.html")


from PIL import Image

def agregar_firma(ruta_pdf, firma_nombre):
    """ Agrega la firma en la parte inferior derecha de todas las páginas sin modificar su tamaño """
    doc = fitz.open(ruta_pdf)

    # Obtener la ruta de la firma
    firma_path = os.path.join(settings.MEDIA_ROOT, "firmas", firma_nombre)
    if not os.path.exists(firma_path):
        raise FileNotFoundError(f"La firma {firma_nombre} no existe en media/firmas/")

    # Obtener dimensiones reales de la imagen de la firma
    with Image.open(firma_path) as img:
        firma_ancho, firma_alto = img.size

    # Factor de conversión de píxeles a puntos PDF
    factor_conversion = 0.50  # Ajuste aproximado para DPI de 72 puntos por pulgada
    firma_ancho *= factor_conversion
    firma_alto *= factor_conversion

    # Insertar firma en la parte inferior derecha de todas las páginas
    for page in doc:
        ancho_pagina = page.rect.width
        alto_pagina = page.rect.height

        # Definir la posición en la esquina inferior derecha sin cambiar el tamaño
        margen_inferior = 20  # Ajusta la distancia desde el borde inferior
        margen_derecho = 10   # Ajusta la distancia desde el borde derecho

        rect = fitz.Rect(
            ancho_pagina - firma_ancho - margen_derecho,  # X inicial (derecha)
            alto_pagina - firma_alto - margen_inferior,   # Y inicial (inferior)
            ancho_pagina - margen_derecho,               # X final
            alto_pagina - margen_inferior                # Y final
        )

        page.insert_image(rect, filename=firma_path, keep_proportion=True)

    # Guardar en memoria el nuevo PDF con firma
    pdf_output = io.BytesIO()
    doc.save(pdf_output)
    pdf_output.seek(0)
    return pdf_output
