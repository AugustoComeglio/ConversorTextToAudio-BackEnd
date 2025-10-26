from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from gtts import gTTS
from gtts.lang import tts_langs  # Importamos la función para obtener idiomas
import uuid
import os

app = FastAPI(
    title="Conversor - Text to Audio",
    version="1.1",
    description="API para convertir texto a audio con gTTS y listar opciones."
)

# Carpeta temporal para guardar los audios
OUTPUT_DIR = "audios"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Funciones de Utilidad ---
def cleanup_file(filepath: str):
    """
    Elimina un archivo del servidor después de ser enviado en la respuesta.
    """
    try:
        os.remove(filepath)
        print(f"Archivo temporal eliminado: {filepath}")
    except OSError as e:
        print(f"Error al eliminar el archivo {filepath}: {e}")


# --- Endpoints de Opciones ---

@app.get("/idiomas")
async def get_idiomas():
    """
    Devuelve un diccionario con todos los idiomas (y sus códigos)
    soportados por gTTS.
    """
    return tts_langs()

@app.get("/formatos")
async def get_formatos():
    """
    Devuelve los formatos de audio que esta API puede generar.
    (gTTS nativamente solo genera MP3)
    """
    return [
        {"id": "mp3", "nombre": "MPEG Audio Layer III (MP3)"}
    ]

@app.get("/opciones-disponibles")
async def get_opciones_disponibles():
    """
    Endpoint principal para un frontend.
    Devuelve todas las opciones de personalización en un solo JSON.
    """
    # Los TLDs (Top-Level Domains) controlan el acento/voz regional.
    # Esta lista se basa en la documentación de gTTS.
    acentos_tlds = {
        "com.ar": "Español (Argentina)",
        "es": "Español (España)",
        "com.mx": "Español (México)",
        "com.us": "Español (Estados Unidos)",
        "com": "Inglés (EEUU)",
        "co.uk": "Inglés (Reino Unido)",
        "com.au": "Inglés (Australia)",
        "ca": "Inglés (Canadá)",
        "co.in": "Inglés (India)",
        "ie": "Inglés (Irlanda)",
        "co.za": "Inglés (Sudáfrica)",
        "fr": "Francés (Francia)",
        "com.br": "Portugués (Brasil)",
        "pt": "Portugués (Portugal)",
        "it": "Italiano",
        "de": "Alemán",
        # Puedes añadir más TLDs soportados por gTTS si lo deseas
    }

    velocidades = [
        {"id": False, "nombre": "Normal"},
        {"id": True, "nombre": "Lento"}
    ]

    return {
        "idiomas": tts_langs(),
        "formatos": await get_formatos(),
        "acentos_tlds": acentos_tlds,
        "velocidades": velocidades
    }

# --- Endpoint de Generación (Actualizado) ---

@app.post("/generar-audio")
async def generar_audio(
    texto: str = Form(...),
    lang: str = Form('es'),
    tld: str = Form('com.ar'),
    slow: bool = Form(False)
):
    """
    Convierte el texto recibido en un archivo MP3 y lo devuelve.
    Ahora acepta parámetros para personalizar el idioma, acento (tld) y velocidad.
    """
    # Crear un nombre único para el archivo usando UUID
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        # Generar el audio con los parámetros recibidos
        tts = gTTS(text=texto, lang=lang, tld=tld, slow=slow)
        tts.save(filepath)

        # Devolver el archivo generado y programar su eliminación
        return FileResponse(
            filepath,
            media_type="audio/mp3",
            filename=f"audio_generado.mp3", # Nombre que verá el usuario al descargar
            background=BackgroundTask(cleanup_file, filepath),
            content_disposition_type="inline"  # <-- AÑADIDO: Sugiere al navegador reproducir
        )
    except Exception as e:
        # Manejo básico de errores (ej. idioma no soportado)
        return {"error": str(e)}, 400
