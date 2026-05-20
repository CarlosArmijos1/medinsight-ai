import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_lab_results(data: dict) -> str:
    paciente = data.get("paciente", {})
    examenes = data.get("examenes", [])
    
    # Construir resumen de examenes para el prompt
    examenes_texto = ""
    for e in examenes:
        estado = e.get("estado", "normal")
        flag = "[ALTO]" if estado == "alto" else "[BAJO]" if estado == "bajo" else ""
        examenes_texto += f"- {e['nombre']}: {e['resultado']} {e['unidad']} (Ref: {e['referencia']}) {flag}\n"
    
    prompt = f"""Eres un medico internista experto analizando resultados de laboratorio.

PACIENTE:
- Nombre: {paciente.get('nombre')}
- Edad: {paciente.get('edad')} años
- Sexo: {paciente.get('sexo')}
- Fecha: {paciente.get('fecha')}

RESULTADOS:
{examenes_texto}

Genera un informe clinico estructurado con exactamente estas secciones:

1. RESUMEN GENERAL
Estado global del paciente en 2-3 oraciones.

2. HALLAZGOS RELEVANTES
Por cada valor alterado:
- Que significa clinicamente
- Posibles causas mas probables
- Si requiere atencion inmediata o seguimiento

3. VALORES NORMALES DESTACABLES
Menciona brevemente los valores que confirman buen estado de salud.

4. RECOMENDACIONES PARA EL MEDICO
Examenes complementarios sugeridos, preguntas a hacer al paciente, posibles diagnosticos diferenciales.

5. NIVEL DE URGENCIA
Verde (control rutinario) / Amarillo (seguimiento en 1-2 semanas) / Rojo (atencion inmediata)

Sé preciso, tecnico y conciso. Este informe es para un medico, no para el paciente."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    
    return response.choices[0].message.content