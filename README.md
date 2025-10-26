# ConversorTextToAudio-BackEnd
## Descripción
Conversor - Text to Audio (Versión 1.2) es una API de backend diseñada para convertir texto en audio utilizando la biblioteca gTTS (Google Text-to-Speech).

La API no solo genera el audio, sino que también proporciona una serie de endpoints para descubrir las opciones de personalización disponibles, como idiomas, acentos (TLDs) y velocidades de habla. Está construida con FastAPI, lo que garantiza un alto rendimiento y una documentación de API interactiva generada automáticamente.

El sistema está configurado con CORS (Cross-Origin Resource Sharing) para permitir solicitudes desde orígenes específicos (como http://localhost:5173), facilitando su integración con aplicaciones frontend (como React, Vue, etc.).

## Tecnologías Utilizadas
- Python 3: Lenguaje de programación base.
- FastAPI: Framework web moderno y de alto rendimiento para construir las API.
- gTTS (Google Text-to-Speech): Biblioteca para interactuar con la API de Google Translate y generar el audio a partir de texto.
- Uvicorn: Servidor ASGI (Asynchronous Server Gateway Interface) para ejecutar la aplicación FastAPI.

## Características Principales
- Conversión de Texto a Audio: Endpoint principal para generar archivos MP3 a partir de un texto.
- Personalización de Audio: Permite especificar el idioma (lang), el acento/dominio (tld) y la velocidad (slow) del audio generado.
- Endpoints de Descubrimiento: Proporciona endpoints GET para que el frontend pueda consultar dinámicamente los idiomas, formatos, acentos y velocidades soportados.
- Manejo Eficiente de Archivos: Genera archivos de audio con un nombre único (UUID) en un directorio temporal (/audios).
- Autolimpieza: Utiliza BackgroundTask de Starlette para eliminar automáticamente el archivo de audio del servidor después de ser enviado al cliente, evitando la acumulación de archivos.
- Documentación Automática: Incluye documentación interactiva de la API (Swagger UI y ReDoc) generada automáticamente por FastAPI.

## Instalación y Puesta en Marcha
### Clonar el repositorio:
```
git clone [URL-DE-TU-REPOSITORIO]
cd ConversorTextToAudio-BackEnd
```
### Crear y activar un entorno virtual:
```
# Para Windows
python -m venv venv
venv\Scripts\activate

# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
### Instalar las dependencias: (Se recomienda crear un archivo requirements.txt con el siguiente contenido)
```
fastapi
uvicorn[standard]
gTTS
```
### Luego, instalar con:
```
pip install -r requirements.txt
```
### O instalar manualmente:
```
pip install fastapi uvicorn gtts
```
### Ejecutar la aplicación:
```
# El comando 'main' se refiere a 'main.py' y 'app' al objeto FastAPI = FastAPI()
uvicorn main:app --reload
```
El servidor estará activo en http://127.0.0.1:8000.

## Documentación de la API
Una vez que el servidor esté en funcionamiento, puedes acceder a la documentación interactiva de la API generada por FastAPI en las siguientes rutas:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints de la API
### Opciones de Generación
```
GET /idiomas
```
Devuelve una lista de objetos JSON con todos los idiomas (id y nombre) soportados por gTTS.

Respuesta de ejemplo:

```
[
  {"id": "es", "nombre": "Spanish"},
  {"id": "en", "nombre": "English"},
  {"id": "fr", "nombre": "French"}
  ...
]
```
```
GET /formatos
```
Devuelve los formatos de audio que la API puede generar. (gTTS nativamente solo genera MP3).

Respuesta de ejemplo:
```
[
  {"id": "mp3", "nombre": "MPEG Audio Layer III (MP3)"}
]
```
```
GET /acentos
```
Devuelve la lista de acentos (TLDs) disponibles. Opcionalmente, acepta un parámetro de consulta lang para filtrar los acentos por idioma.

```
Ejemplo de solicitud (sin filtro): http://127.0.0.1:8000/acentos

Ejemplo de solicitud (filtrada): http://127.0.0.1:8000/acentos?lang=es
```

Respuesta de ejemplo (filtrada por lang=es):
```
[
  {"id": "com.ar", "nombre": "Español (Argentina)", "lang": "es"},
  {"id": "es", "nombre": "Español (España)", "lang": "es"},
  {"id": "com.mx", "nombre": "Español (México)", "lang": "es"},
  {"id": "com.us", "nombre": "Español (Estados Unidos)", "lang": "es"}
]
```
```
GET /velocidades
```
Devuelve las velocidades de habla disponibles (Normal o Lento).

Respuesta de ejemplo:
```
[
  {"id": false, "nombre": "Normal"},
  {"id": true, "nombre": "Lento"}
]
```
Generación de Audio
```
POST /generar-audio
```
Convierte el texto recibido en un archivo MP3 y lo devuelve. Acepta los parámetros como Form Data.

### Parámetros (Form Data):

- texto (str, requerido): El texto que se desea convertir a audio.
- lang (str, opcional, default: 'es'): El código del idioma (ej: 'en', 'fr').
- tld (str, opcional, default: 'com.ar'): El dominio de Google a utilizar, que define el acento (ej: 'com.mx', 'co.uk').
- slow (bool, opcional, default: False): Si es True, genera el audio a una velocidad más lenta.

### Respuesta Exitosa:

- Código 200 OK.
- El cuerpo de la respuesta es el archivo de audio (audio/mp3).
- El archivo se devuelve como inline, sugiriendo al navegador que lo reproduzca en lugar de descargarlo.

### Respuesta de Error:
- Código 400 Bad Request si ocurre un error (ej. idioma no soportado).
- Cuerpo de la respuesta: {"error": "Descripción del error"}.