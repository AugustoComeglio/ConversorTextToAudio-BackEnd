from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from gtts import gTTS
import uuid
import os

app = FastAPI(title="Conversor - Text to Audio", version="1.0")

# Carpeta temporal para guardar los audios
OUTPUT_DIR = "audios"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/generar-audio")
async def generar_audio(texto: str = Form(...)):
    """
    Convierte el texto recibido en un archivo MP3 y lo devuelve.
    """
    # Crear un nombre único para el archivo
    filename = f"Audio.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Generar el audio con voz femenina (es-AR = español de Argentina)
    tts = gTTS(text=texto, lang='es', tld='com.ar', slow=False)
    tts.save(filepath)

    # Devolver el archivo generado
    return FileResponse(filepath, media_type="audio/mp3", filename=filename)