# Implementación alternativa para index2.html
import io
import os
import comtypes.client
import pythoncom
from reportlab.pdfgen import canvas
from django.http import FileResponse
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings

def firmar_documento_alternativo(request):

    if request.method == "POST" and request.FILES.get("archivo"):        
        pythoncom.CoInitialize()  # 🔹 Inicializa COM antes de usar Word

        archivo_word = request.FILES["archivo"]
        firma_nombre = request.POST.get("firma")
        print("Recibido archivo para index2.html")
        
        if not archivo_word.name.endswith(".docx"):
            print("Error: El archivo no es un .docx")
            return render(request, "index2.html", {"error": "El archivo debe ser un documento .docx"})
        
        ruta_word = default_storage.save("temp.docx", archivo_word)
        ruta_word_absoluta = default_storage.path(ruta_word)
        ruta_pdf = ruta_word_absoluta.replace(".docx", ".pdf")
        
        try:
            word = comtypes.client.CreateObject('Word.Application')
            word.Visible = False  # 🔹 Evita que se abra la interfaz de Word
            doc = word.Documents.Open(ruta_word_absoluta)
            doc.SaveAs(ruta_pdf, FileFormat=17)
            doc.Close()
            word.Quit()
            print("Conversión con comtypes exitosa")
            
            pdf_firmado = agregar_firma_alternativa(ruta_pdf, firma_nombre)
            response = FileResponse(pdf_firmado, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="documento_firmado_alternativa.pdf"'
        
        finally:
            pythoncom.CoUninitialize()  # 🔹 Cierra el entorno COM
            if os.path.exists(ruta_word_absoluta):
                os.remove(ruta_word_absoluta)
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
                
        return response
    return render(request, "index2.html")

def agregar_firma_alternativa(ruta_pdf, firma_nombre):
    print("Agregando firma en index2.html")
    firma_path = os.path.join(settings.MEDIA_ROOT, "firmas", firma_nombre)
    
    if not os.path.exists(firma_path):
        print(f"Error: No se encontró la firma en {firma_path}")
        raise FileNotFoundError(f"La firma {firma_nombre} no existe en media/firmas/")

    pdf_output = io.BytesIO()
    c = canvas.Canvas(pdf_output)
    c.drawImage(firma_path, 400, 50, width=100, height=50, mask='auto')
    c.save()
    pdf_output.seek(0)
    return pdf_output
