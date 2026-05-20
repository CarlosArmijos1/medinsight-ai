import streamlit.components.v1 as components
import streamlit as st
import os
import unicodedata
from dotenv import load_dotenv
from extractor.image_extractor import extract_lab_data
from analyzer.clinical_analyzer import analyze_lab_results
from rag.rag_engine import build_collection, query_evidence

load_dotenv()

# ── Estilos ────────────────────────────────────────────────
st.set_page_config(page_title="MedInsight AI", layout="wide", page_icon="🧬")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

h1, h2, h3 { font-family: 'DM Serif Display', serif; }

.main { padding: 2rem 3rem; }

.header-box {
    background: linear-gradient(135deg, #0d1f2d 0%, #112233 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.header-box::before {
    content: "🧬";
    font-size: 8rem;
    position: absolute;
    right: -1rem;
    top: -1rem;
    opacity: 0.06;
}

.header-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    background: linear-gradient(90deg, #58a6ff, #79c0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.header-sub {
    color: #8b949e;
    font-size: 1rem;
    margin-top: 0.5rem;
    font-weight: 300;
}

.upload-box {
    border: 2px dashed #1e3a5f;
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    background: #0d1f2d;
    margin-bottom: 1.5rem;
}

.upload-icon { font-size: 3rem; margin-bottom: 1rem; }
.upload-title { font-size: 1.3rem; font-weight: 600; color: #e6edf3; }
.upload-sub { color: #8b949e; font-size: 0.9rem; margin-top: 0.5rem; }

.section-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #58a6ff;
    border-bottom: 1px solid #21262d;
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
}

.patient-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 0.5rem;
}

.patient-card {
    background: #0d1f2d;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}

.patient-label { font-size: 0.75rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.1em; }
.patient-value { font-size: 1.1rem; font-weight: 600; color: #e6edf3; margin-top: 0.3rem; }

.exam-row {
    display: flex;
    align-items: center;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.3rem;
    transition: background 0.2s;
}
.exam-row:hover { background: #1c2128; }
.exam-name { flex: 3; font-weight: 500; }
.exam-val { flex: 1; font-weight: 700; text-align: center; }
.exam-ref { flex: 2; color: #8b949e; font-size: 0.85rem; text-align: center; }
.exam-unit { flex: 1; color: #8b949e; font-size: 0.85rem; text-align: right; }

.badge-normal { color: #3fb950; }
.badge-alto { color: #f85149; }
.badge-bajo { color: #58a6ff; }
.badge-nd { color: #8b949e; }

.alert-card {
    background: #2d1b1b;
    border: 1px solid #5a1d1d;
    border-left: 4px solid #f85149;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}

.alert-card.bajo {
    background: #0d1f2d;
    border-color: #1e3a5f;
    border-left-color: #58a6ff;
}

.pubmed-card {
    background: #0d1f2d;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}

.pubmed-title { font-weight: 600; color: #e6edf3; margin-bottom: 0.4rem; }
.pubmed-abstract { color: #8b949e; font-size: 0.88rem; line-height: 1.6; margin-bottom: 0.6rem; }
.pubmed-link { color: #58a6ff; font-size: 0.85rem; text-decoration: none; }

.error-box {
    background: #2d1b1b;
    border: 1px solid #5a1d1d;
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
}

.stSpinner > div { border-top-color: #58a6ff !important; }

div[data-testid="stFileUploader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <p class="header-title">MedInsight AI</p>
    <p class="header-sub">Sistema de segunda opinión médica con inteligencia artificial y evidencia científica de PubMed</p>
</div>
""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────
st.markdown("""
<div class="upload-box">
    <div class="upload-icon">📋</div>
    <div class="upload-title">Sube tu resultado de laboratorio</div>
    <div class="upload-sub">Formatos aceptados: JPG, PNG — Hemogramas, bioquímica, urianálisis y más</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed"
)

# ── Utilidades ─────────────────────────────────────────────
traduccion = {
    "cetonas": "ketones", "glucosa": "glucose", "hemoglobina": "hemoglobin",
    "hematocrito": "hematocrit", "leucocitos": "leukocytes", "eosinofilos": "eosinophils",
    "basofilos": "basophils", "linfocitos": "lymphocytes", "monocitos": "monocytes",
    "neutrofilos": "neutrophils", "plaquetas": "platelets", "eritrocitos": "erythrocytes",
    "hematies": "erythrocytes", "creatinina": "creatinine", "urea": "urea",
    "colesterol": "cholesterol", "trigliceridos": "triglycerides", "proteinas": "proteins",
    "bilirrubina": "bilirubin", "albumina": "albumin", "sodio": "sodium",
    "potasio": "potassium", "calcio": "calcium", "fosforo": "phosphorus",
    "acido urico": "uric acid", "ferritina": "ferritin", "hierro": "iron",
    "insulina": "insulin", "cortisol": "cortisol", "tsh": "TSH thyroid",
    "pcr": "C-reactive protein", "vsg": "erythrocyte sedimentation rate",
}

TERMINOS_MEDICOS = [
    "hemoglobina", "hematocrito", "leucocitos", "plaquetas", "glucosa",
    "creatinina", "urea", "colesterol", "trigliceridos", "bilirrubina",
    "eosinofilos", "neutrofilos", "linfocitos", "monocitos", "basofilos",
    "hematies", "eritrocitos", "ferritina", "albumina", "proteinas",
    "sodio", "potasio", "calcio", "tsh", "pcr", "insulina", "cortisol",
    "cetonas", "acido urico", "vsg", "rdw", "vcm", "hcm", "chcm",
    "resultado", "referencia", "valor", "unidad", "examen", "laboratorio",
    "hemograma", "bioquimica", "orina", "sangre", "suero", "plasma",
    "g/dl", "mg/dl", "u/l", "mmol", "10^3", "10^6", "%"
]

def limpiar(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def traducir_termino(nombre: str) -> str:
    nombre_limpio = limpiar(nombre.split("(")[0].strip())
    for es, en in traduccion.items():
        if es in nombre_limpio:
            return en
    return nombre_limpio

def es_resultado_medico(data: dict) -> bool:
    """Verifica que el documento sea un resultado de laboratorio real."""
    examenes = data.get("examenes", [])
    if len(examenes) < 2:
        return False
    texto_total = " ".join([
        limpiar(e.get("nombre", "")) + " " +
        limpiar(str(e.get("resultado", ""))) + " " +
        limpiar(str(e.get("referencia", "")))
        for e in examenes
    ])
    coincidencias = sum(1 for t in TERMINOS_MEDICOS if t in texto_total)
    return coincidencias >= 3

# ── Procesamiento ───────────────────────────────────────────
if uploaded_file:
    file_bytes = uploaded_file.read()

    with st.spinner("Analizando documento con IA..."):
        try:
            data = extract_lab_data(file_bytes)
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <h3>Error al procesar el archivo</h3>
                <p style="color:#8b949e">{e}</p>
            </div>
            """, unsafe_allow_html=True)
            st.stop()

    # Validacion medica
    if not es_resultado_medico(data):
        st.markdown("""
        <div class="error-box">
            <h3 style="color:#f85149">⚠️ Documento no reconocido</h3>
            <p style="color:#8b949e">
                El archivo no parece ser un resultado de laboratorio médico válido.<br><br>
                Asegurate de subir un <strong>hemograma, bioquímica, urianálisis</strong> u otro examen clínico
                con valores numéricos y rangos de referencia.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    examenes = data.get("examenes", [])
    p = data.get("paciente", {})
    anomalos = [e for e in examenes if e.get("estado") in ("alto", "bajo")]

    # ── Paciente ────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Datos del Paciente</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="patient-grid">
        <div class="patient-card">
            <div class="patient-label">Nombre</div>
            <div class="patient-value">{p.get('nombre', '—')}</div>
        </div>
        <div class="patient-card">
            <div class="patient-label">Edad</div>
            <div class="patient-value">{p.get('edad', '—')}</div>
        </div>
        <div class="patient-card">
            <div class="patient-label">Sexo</div>
            <div class="patient-value">{p.get('sexo', '—')}</div>
        </div>
        <div class="patient-card">
            <div class="patient-label">Fecha</div>
            <div class="patient-value">{p.get('fecha', '—')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Resultados ──────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔬 Resultados</div>', unsafe_allow_html=True)

    colores = {"alto": "#f85149", "bajo": "#58a6ff", "normal": "#3fb950"}
    badges = {"alto": "🔴", "bajo": "🔵", "normal": "🟢"}

    table_html = """
    <table style="width:100%;border-collapse:collapse;">
        <thead>
            <tr style="border-bottom:1px solid #21262d;">
                <th style="text-align:left;padding:0.6rem 0.8rem;color:#8b949e;font-size:0.78rem;font-weight:500;text-transform:uppercase;letter-spacing:0.08em;">Examen</th>
                <th style="text-align:center;padding:0.6rem 0.8rem;color:#8b949e;font-size:0.78rem;font-weight:500;text-transform:uppercase;">Resultado</th>
                <th style="text-align:center;padding:0.6rem 0.8rem;color:#8b949e;font-size:0.78rem;font-weight:500;text-transform:uppercase;">Referencia</th>
                <th style="text-align:right;padding:0.6rem 0.8rem;color:#8b949e;font-size:0.78rem;font-weight:500;text-transform:uppercase;">Unidad</th>
            </tr>
        </thead>
        <tbody>
    """

    for ex in examenes:
        estado = ex.get("estado", "normal")
        badge = badges.get(estado, "⚪")
        color = colores.get(estado, "#8b949e")
        table_html += f"""
        <tr style="border-bottom:1px solid #1c2128;">
            <td style="padding:0.65rem 0.8rem;font-weight:500;">{badge} {ex.get('nombre', '')}</td>
            <td style="padding:0.65rem 0.8rem;text-align:center;font-weight:700;color:{color};">{ex.get('resultado', '—')}</td>
            <td style="padding:0.65rem 0.8rem;text-align:center;color:#8b949e;font-size:0.88rem;">{ex.get('referencia', '—')}</td>
            <td style="padding:0.65rem 0.8rem;text-align:right;color:#8b949e;font-size:0.88rem;">{ex.get('unidad', '')}</td>
        </tr>
        """

    table_html += "</tbody></table>"
    components.html(
        f"""
        <style>
        body {{ margin:0; background:#161b22; color:#e6edf3; font-family:'DM Sans',sans-serif; }}
        table {{ width:100%; border-collapse:collapse; }}
        th {{ text-align:left; padding:0.6rem 0.8rem; color:#8b949e; font-size:0.78rem; font-weight:500; text-transform:uppercase; letter-spacing:0.08em; border-bottom:1px solid #21262d; }}
        td {{ padding:0.65rem 0.8rem; border-bottom:1px solid #1c2128; font-size:0.92rem; }}
        </style>
        {table_html}
        """,
        height=len(examenes) * 48 + 60,
        scrolling=False
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Alertas ─────────────────────────────────────────────
    if anomalos:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠️ Valores Fuera de Rango</div>', unsafe_allow_html=True)
        for e in anomalos:
            clase = "bajo" if e.get("estado") == "bajo" else ""
            icono = "🔵" if e.get("estado") == "bajo" else "🔴"
            st.markdown(f"""
            <div class="alert-card {clase}">
                <strong>{icono} {e['nombre']}</strong> &nbsp;
                <span style="font-size:1.1rem;font-weight:700">{e['resultado']}</span>
                <span style="color:#8b949e"> ({e['estado'].upper()}) — Ref: {e['referencia']} {e['unidad']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Análisis clínico ────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🤖 Análisis Clínico IA</div>', unsafe_allow_html=True)
    with st.spinner("Generando análisis clínico..."):
        analisis = analyze_lab_results(data)
    st.markdown(analisis)
    st.markdown('<p style="color:#8b949e;font-size:0.82rem;margin-top:1rem">⚠️ Este análisis es orientativo. No reemplaza el criterio médico profesional.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Evidencia PubMed ────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📚 Evidencia Científica (PubMed)</div>', unsafe_allow_html=True)

    if anomalos:
        hallazgos_queries = [
            f"{traducir_termino(e['nombre'])} {e['estado']} clinical significance"
            for e in anomalos
        ]

        with st.spinner("Buscando evidencia en PubMed..."):
            collection = build_collection(hallazgos_queries)
            query_general = " ".join([traducir_termino(e["nombre"]) for e in anomalos])
            evidencia = query_evidence(collection, query_general, n_results=5)

        if evidencia:
            for art in evidencia:
                st.markdown(f"""
                <div class="pubmed-card">
                    <div class="pubmed-title">📄 {art['title']} <span style="color:#8b949e;font-weight:400">({art['year']})</span></div>
                    <div class="pubmed-abstract">{art['abstract']}</div>
                    <a class="pubmed-link" href="{art['url']}" target="_blank">Ver artículo completo en PubMed →</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#8b949e">No se encontró evidencia relevante para los hallazgos actuales.</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#3fb950">✅ Todos los valores dentro del rango normal. Sin evidencia específica requerida.</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)