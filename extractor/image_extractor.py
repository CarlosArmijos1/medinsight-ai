import base64
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def encode_image(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")

def extract_lab_data(file_bytes: bytes) -> dict:
    base64_image = encode_image(file_bytes)
    
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Eres un asistente medico especializado en analisis de laboratorio.
Extrae TODOS los examenes de este resultado de laboratorio.
Responde UNICAMENTE con un JSON valido, sin texto adicional, sin markdown, sin backticks.
Formato exacto:
{
  "paciente": {
    "nombre": "",
    "edad": "",
    "sexo": "",
    "fecha": ""
  },
  "examenes": [
    {
      "nombre": "",
      "resultado": "",
      "referencia": "",
      "unidad": "",
      "estado": "normal|alto|bajo"
    }
  ]
}"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=2000
    )
    
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)