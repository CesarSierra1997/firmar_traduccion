import io
import os
import fitz  # PyMuPDF
from win32com import client as pythoncom
from django.http import FileResponse
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from docx2pdf import convert
from PIL import Image

def firmar_documento(request):
    pythoncom.CoInitialize()
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo_word = request.FILES["archivo"]
        firma_nombre = request.POST.get("firma")
        print("Recibido archivo para index.html")
        
        if not archivo_word.name.endswith(".docx"):
            print("Error: El archivo no es un .docx")
            return render(request, "index.html", {"error": "El archivo debe ser un documento .docx"})
        
        ruta_word = default_storage.save("temp.docx", archivo_word)
        ruta_word_absoluta = default_storage.path(ruta_word)
        ruta_pdf = ruta_word_absoluta.replace(".docx", ".pdf")
        
        try:
            convert(ruta_word_absoluta, ruta_pdf)
            print("Conversión exitosa a PDF")
            
            pdf_firmado = agregar_firma(ruta_pdf, firma_nombre)
            response = FileResponse(pdf_firmado, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="documento_firmado.pdf"'
        
        finally:
            if os.path.exists(ruta_word_absoluta):
                os.remove(ruta_word_absoluta)
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
                
        return response
    return render(request, "index.html")

def agregar_firma(ruta_pdf, firma_nombre):
    print("Agregando firma en index.html")
    doc = fitz.open(ruta_pdf)
    firma_path = os.path.join(settings.MEDIA_ROOT, "firmas", firma_nombre)
    
    if not os.path.exists(firma_path):
        print(f"Error: No se encontró la firma en {firma_path}")
        raise FileNotFoundError(f"La firma {firma_nombre} no existe en media/firmas/")
    
    with Image.open(firma_path) as img:
        firma_ancho, firma_alto = img.size
    
    factor_conversion = 0.50
    firma_ancho *= factor_conversion
    firma_alto *= factor_conversion
    
    for page in doc:
        ancho_pagina = page.rect.width
        alto_pagina = page.rect.height
        
        margen_inferior = 20
        margen_derecho = 10
        
        rect = fitz.Rect(
            ancho_pagina - firma_ancho - margen_derecho,
            alto_pagina - firma_alto - margen_inferior,
            ancho_pagina - margen_derecho,
            alto_pagina - margen_inferior
        )
        
        page.insert_image(rect, filename=firma_path, keep_proportion=True)
    
    pdf_output = io.BytesIO()
    doc.save(pdf_output)
    pdf_output.seek(0)
    return pdf_output

