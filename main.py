from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from gtts import gTTS
from gtts.lang import tts_langs  # Importamos la función para obtener idiomas
import uuid
import os
from typing import Optional # Importamos Optional para el parámetro de consulta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Conversor - Text to Audio",
    version="1.2", # Versión actualizada
    description="API para convertir texto a audio con gTTS y listar opciones."
)

# --- INICIO DE LA CONFIGURACIÓN DE CORS ---

# Lista de orígenes (dominios/puertos) que tienen permiso para hablar con tu API
origins = [
    "http://localhost:5173",  # El origen de tu app de React (según el error)
    "http://localhost",
    "http://1.27.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Permite los orígenes en la lista
    allow_credentials=True,   # Permite cookies (si las usaras)
    allow_methods=["*"],      # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],      # Permite todos los headers
)
# --- FIN DE LA CONFIGURACIÓN DE CORS ---

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
    Devuelve una LISTA de objetos con todos los idiomas (id, nombre)
    soportados por gTTS.
    """
    # tts_langs() devuelve un diccionario, ej: {'es': 'Spanish', 'en': 'English'}
    # Lo convertimos a una lista de objetos para consistencia con los otros endpoints.
    langs_dict = tts_langs()
    return [{"id": lang_code, "nombre": lang_name} for lang_code, lang_name in langs_dict.items()]

@app.get("/formatos")
async def get_formatos():
    """
    Devuelve los formatos de audio que esta API puede generar.
    (gTTS nativamente solo genera MP3)
    """
    return [
        {"id": "mp3", "nombre": "MPEG Audio Layer III (MP3)"}
    ]

@app.get("/acentos")
async def get_acentos(lang: Optional[str] = None): # Acepta un parámetro 'lang' opcional
    """
    Devuelve la lista de acentos (TLDs) disponibles.
    Si se provee el parámetro 'lang' (ej: /acentos?lang=es),
    filtrará y devolverá solo los acentos para ese idioma.
    """
    
    # Lista maestra de acentos con su idioma correspondiente
    acentos_tlds = [
        # --- Español (es) ---
        {"Id": "com.ar", "nombre": "Español (Argentina)", "lang": "es"},
        {"Id": "es", "nombre": "Español (España)", "lang": "es"},
        {"Id": "com.mx", "nombre": "Español (México)", "lang": "es"},
        {"Id": "com.us", "nombre": "Español (Estados Unidos)", "lang": "es"},
        
        # --- Inglés (en) ---
        {"Id": "com", "nombre": "Inglés (EEUU)", "lang": "en"},
        {"Id": "co.uk", "nombre": "Inglés (Reino Unido)", "lang": "en"},
        {"Id": "com.au", "nombre": "Inglés (Australia)", "lang": "en"},
        {"Id": "ca", "nombre": "Inglés (Canadá)", "lang": "en"},
        {"Id": "co.in", "nombre": "Inglés (India)", "lang": "en"},
        {"Id": "ie", "nombre": "Inglés (Irlanda)", "lang": "en"},
        {"Id": "co.za", "nombre": "Inglés (Sudáfrica)", "lang": "en"},
        
        # --- Portugués (pt) ---
        {"Id": "com.br", "nombre": "Portugués (Brasil)", "lang": "pt"},
        {"Id": "pt", "nombre": "Portugués (Portugal)", "lang": "pt"},
        
        # --- Chino (zh-cn, zh-tw) ---
        {"Id": "zh-cn", "nombre": "Chino (Mandarin/China)", "lang": "zh-cn"},
        {"Id": "zh-tw", "nombre": "Chino (Mandarin/Taiwan)", "lang": "zh-tw"},
        
        # --- Otros ---
        {"Id": "fr", "nombre": "Francés (Francia)", "lang": "fr"},
        {"Id": "it", "nombre": "Italiano (Italia)", "lang": "it"},
        {"Id": "de", "nombre": "Alemán (Alemania)", "lang": "de"},
        {"Id": "ja", "nombre": "Japonés (Japón)", "lang": "ja"},
        {"Id": "ko", "nombre": "Coreano (Corea)", "lang": "ko"},
        {"Id": "ru", "nombre": "Ruso (Rusia)", "lang": "ru"},
        {"Id": "nl", "nombre": "Holandés (Países Bajos)", "lang": "nl"},
        {"Id": "pl", "nombre": "Polaco (Polonia)", "lang": "pl"},
        {"Id": "com.vn", "nombre": "Vietnamita (Vietnam)", "lang": "vi"},
        {"Id": "com.tr", "nombre": "Turco (Turquía)", "lang": "tr"},
        {"Id": "com.gr", "nombre": "Griego (Grecia)", "lang": "el"},
        {"Id": "co.th", "nombre": "Tailandés (Tailandia)", "lang": "th"}
    ]

    # Si el usuario NO especificó un idioma, devolvemos toda la lista
    if not lang:
        return acentos_tlds

    # Si el usuario especificó un idioma, filtramos la lista
    filtered_acentos = [
        acento for acento in acentos_tlds if acento["lang"] == lang
    ]
    
    return filtered_acentos

@app.get("/velocidades")
async def get_velocidades():
    """
    Devuelve las velocidades de habla disponibles.
    """
    velocidades = [
        {"id": False, "nombre": "Normal"},
        {"id": True, "nombre": "Lento"}
    ]
    return velocidades


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