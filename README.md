# 🧬 MedInsight AI

Sistema de segunda opinión médica con inteligencia artificial que analiza resultados de laboratorio, genera análisis clínicos y busca evidencia científica en PubMed automáticamente.

---

## ✨ Características

- **Extracción inteligente** — Vision AI (Llama 4) lee hemogramas, bioquímicas y urianálisis directamente desde imágenes
- **Análisis clínico** — LLM especializado genera hallazgos, diagnósticos diferenciales y nivel de urgencia
- **RAG sobre PubMed** — Busca y vectoriza artículos científicos reales relacionados a los hallazgos del paciente
- **Validación médica** — Rechaza documentos que no sean resultados de laboratorio válidos
- **Interfaz profesional** — Dashboard oscuro con clasificación visual de valores alterados

---

## 🏗️ Arquitectura

```
Imagen de laboratorio
        ↓
Groq Vision (Llama 4 Scout) — Extracción estructurada en JSON
        ↓
Validación médica — Verifica que sea un resultado clínico real
        ↓
Groq LLM (Llama 3.3 70B) — Análisis clínico estructurado
        ↓
PubMed API → ChromaDB (embeddings) → RAG — Evidencia científica relevante
        ↓
Dashboard Streamlit
```

---

## 🛠️ Stack

| Componente | Tecnología |
|---|---|
| Vision / LLM | Groq API (Llama 4 Scout + Llama 3.3 70B) |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| Vector store | ChromaDB |
| Evidencia científica | PubMed API (NCBI Entrez) |
| Frontend | Streamlit |
| Lenguaje | Python 3.11+ |

---

## 🚀 Instalación

```bash
git clone https://github.com/CarlosArmijos1/medinsight-ai.git
cd medinsight-ai
pip install -r requirements.txt
```

Creá un archivo `.env`:
```
GROQ_API_KEY=tu_api_key_aqui
```

Correlo:
```bash
python -m streamlit run app.py
```

---

## 📋 Uso

1. Subí una imagen JPG/PNG de un resultado de laboratorio
2. El sistema extrae automáticamente todos los valores
3. Clasifica los valores como normal / alto / bajo
4. Genera un informe clínico con hallazgos y recomendaciones
5. Busca artículos científicos de PubMed relacionados a los valores alterados

---

## 🔬 Tipos de exámenes soportados

- Hemograma completo
- Bioquímica sanguínea
- Urianálisis
- Panel metabólico
- Perfil lipídico
- Y más...

---

## ⚠️ Disclaimer

Este sistema es una herramienta de apoyo informativo. No reemplaza el criterio de un médico profesional. No debe usarse para autodiagnóstico ni como única fuente de decisión clínica.

---

## 👨‍💻 Autor

**Carlos Armijos** — Ing. Ciencias de la Computación, especialización en Sistemas Inteligentes

[![GitHub](https://img.shields.io/badge/GitHub-CarlosArmijos1-181717?logo=github)](https://github.com/CarlosArmijos1)
