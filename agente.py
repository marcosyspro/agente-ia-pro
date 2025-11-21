import streamlit as st
from groq import Groq
import pandas as pd
import PyPDF2
import time

# --- 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero) ---
st.set_page_config(
    page_title="NEXUS AI | Enterprise Solution", 
    page_icon="💠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. INYECCIÓN DE CSS AVANZADO (DISEÑO VISUAL) ---
# Esto es lo que hace que se vea "Pro" y tenga animaciones
st.markdown("""
<style>
    /* Fondo general oscuro profesional */
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(circle at 50% 0%, #1c2331 0%, #0e1117 70%);
    }

    /* Animación de flotación para las tarjetas */
    @keyframes float {
        0% { transform: translateY(0px); box-shadow: 0 5px 15px 0px rgba(0,0,0,0.6); }
        50% { transform: translateY(-15px); box-shadow: 0 25px 15px 0px rgba(0,0,0,0.2); }
        100% { transform: translateY(0px); box-shadow: 0 5px 15px 0px rgba(0,0,0,0.6); }
    }

    /* Estilo de las Tarjetas de Precio (Glassmorphism) */
    .pricing-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .pricing-card:hover {
        border-color: #00d2ff;
        transform: scale(1.02);
    }
    
    /* Animación flotante solo para las tarjetas destacadas */
    .float-animate {
        animation: float 4s ease-in-out infinite;
    }

    /* Títulos y textos */
    .tier-title { font-size: 1.8rem; font-weight: 800; color: #fff; margin-bottom: 10px; }
    .price { font-size: 2.5rem; font-weight: 700; color: #00d2ff; margin: 20px 0; }
    .feature-list { list-style: none; padding: 0; color: #ccc; text-align: left; font-size: 0.9rem; }
    .feature-list li { margin-bottom: 8px; padding-left: 20px; position: relative; }
    .feature-list li::before { content: "✓"; color: #00d2ff; position: absolute; left: 0; }
    
    /* Botones personalizados */
    .custom-button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        border: none;
        padding: 10px 20px;
        color: white;
        border-radius: 50px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin-top: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Iconos Dinámicos (Simulados con Emojis grandes) */
    .icon-large { font-size: 4rem; margin-bottom: 10px; display: block; }

</style>
""", unsafe_allow_html=True)

# --- 3. GESTIÓN DE ESTADO (MEMORIA Y PLAN) ---
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "FREE" # Por defecto entra como Free
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- 4. FUNCIONES DEL BACKEND ---
def procesar_texto(archivo):
    texto = ""
    try:
        if archivo.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(archivo)
            for page in reader.pages: texto += page.extract_text() or ""
        elif archivo.name.endswith(('.xlsx', '.xls', '.csv')):
            df = pd.read_excel(archivo) if archivo.name.endswith('x') else pd.read_csv(archivo)
            texto = df.to_string()
        return texto
    except Exception as e: return str(e)

def get_model_by_tier(tier):
    # Modelos más potentes según el plan
    if tier == "FREE": return "llama3-8b-8192" # Rápido, básico
    if tier == "BASIC": return "llama-3.3-70b-versatile" # Bueno
    if tier == "PRO" or tier == "PREMIUM": return "llama-3.3-70b-versatile" # El mejor
    return "llama3-8b-8192"

def get_system_prompt(tier):
    base = "Eres NEXUS, una IA avanzada."
    if tier == "FREE": return base + " Responde brevemente."
    if tier == "BASIC": return base + " Eres detallado y servicial."
    if tier == "PRO": return base + " Eres un experto analista de datos. Usa formato Markdown avanzado."
    if tier == "PREMIUM": return base + " Eres un Consultor Estratégico de Nivel Ejecutivo. Tus respuestas son profundas, estratégicas y visionarias."
    return base

# --- 5. INTERFAZ: PANTALLA DE SELECCIÓN DE PLANES ---
# Si el usuario no ha seleccionado plan o quiere cambiar, mostramos esto
def mostrar_precios():
    st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 50px;'>Selecciona tu Nivel de Inteligencia</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # --- PLAN FREE ---
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <span class="icon-large">🌱</span>
            <div class="tier-title">FREE</div>
            <div class="price">$0</div>
            <ul class="feature-list">
                <li>IA Básica (Llama 8B)</li>
                <li>Respuestas cortas</li>
                <li>Sin análisis de archivos</li>
                <li>Velocidad estándar</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Elegir FREE", key="btn_free"):
            st.session_state.user_tier = "FREE"
            st.rerun()

    # --- PLAN BASIC ---
    with col2:
        st.markdown("""
        <div class="pricing-card">
            <span class="icon-large">🚀</span>
            <div class="tier-title">BASIC</div>
            <div class="price">$9<small>/m</small></div>
            <ul class="feature-list">
                <li>IA Avanzada (Llama 70B)</li>
                <li>Memoria extendida</li>
                <li>Respuestas detalladas</li>
                <li>Soporte Prioritario</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Elegir BASIC", key="btn_basic"):
            st.session_state.user_tier = "BASIC"
            st.rerun()

    # --- PLAN PRO (Flotante) ---
    with col3:
        st.markdown("""
        <div class="pricing-card float-animate" style="border-color: #00d2ff; box-shadow: 0 0 20px rgba(0, 210, 255, 0.3);">
            <div style="position:absolute; top:0; right:0; background:#00d2ff; color:black; padding:5px 15px; font-weight:bold; font-size:0.8rem;">POPULAR</div>
            <span class="icon-large">💎</span>
            <div class="tier-title">PRO</div>
            <div class="price">$29<small>/m</small></div>
            <ul class="feature-list">
                <li><b>Análisis de Documentos</b></li>
                <li>Lectura de PDF/Excel</li>
                <li>Modo Analista de Datos</li>
                <li>Alta Velocidad</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Elegir PRO", key="btn_pro"):
            st.session_state.user_tier = "PRO"
            st.rerun()

    # --- PLAN PREMIUM ---
    with col4:
        st.markdown("""
        <div class="pricing-card">
            <span class="icon-large">👑</span>
            <div class="tier-title">PREMIUM</div>
            <div class="price">$99<small>/m</small></div>
            <ul class="feature-list">
                <li><b>Todo lo de PRO</b></li>
                <li>Consultor Estratégico</li>
                <li>Privacidad Empresarial</li>
                <li>API Dedicada</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Elegir PREMIUM", key="btn_premium"):
            st.session_state.user_tier = "PREMIUM"
            st.rerun()

# --- 6. BARRA LATERAL (CONTROL CENTER) ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #00d2ff; margin:0;">PLAN ACTUAL</h3>
        <h1 style="color: white; font-size: 3rem; margin:0;">{st.session_state.user_tier}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuración de API
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        api_key = st.text_input("🔑 API Key (Groq):", type="password")

    # Área de subida de archivos (SOLO PARA PRO Y PREMIUM)
    uploaded_file = None
    if st.session_state.user_tier in ["PRO", "PREMIUM"]:
        st.markdown("### 📂 Centro de Datos")
        uploaded_file = st.file_uploader("Analizar Documento", type=["pdf", "xlsx", "csv"])
    elif st.session_state.user_tier in ["FREE", "BASIC"]:
        st.markdown("### 🔒 Centro de Datos")
        st.info(f"Subida de archivos bloqueada en plan {st.session_state.user_tier}. Actualiza a PRO.")

    st.markdown("---")
    if st.button("🔄 Cambiar de Plan"):
        st.session_state.user_tier = "SELECCIONANDO"
        st.rerun()
        
    if st.button("🗑️ Borrar Memoria"):
        st.session_state.mensajes = []
        st.rerun()

# --- 7. LÓGICA PRINCIPAL ---

# Si el usuario está eligiendo plan, mostramos la tabla de precios
if st.session_state.user_tier == "SELECCIONANDO":
    mostrar_precios()

# Si ya tiene plan, mostramos el Chat
else:
    # Encabezado del chat
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom: 20px;">
        <span style="font-size: 2.5rem; margin-right: 15px;">💠</span>
        <div>
            <h1 style="margin:0; font-size: 2rem;">NEXUS AI</h1>
            <span style="color: #00d2ff;">Modo: {get_system_prompt(st.session_state.user_tier).split('.')[1]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Procesamiento de documentos (Si aplica)
    if uploaded_file and api_key:
        file_key = f"processed_{uploaded_file.name}"
        if file_key not in st.session_state:
            with st.spinner("🔄 Procesando datos con motor neuronal..."):
                contenido = procesar_texto(uploaded_file)
                # Inyectar contexto
                st.session_state.mensajes = [{
                    "role": "system", 
                    "content": f"{get_system_prompt(st.session_state.user_tier)} Aquí está el documento: {contenido[:20000]}"
                }]
                st.session_state[file_key] = True
                st.success("✅ Datos integrados en la red neuronal.")

    # Mostrar Historial
    for msj in st.session_state.mensajes:
        if msj["role"] != "system":
            with st.chat_message(msj["role"], avatar="👤" if msj["role"] == "user" else "💠"):
                st.markdown(msj["content"])

    # Input de Chat
    if prompt := st.chat_input("Ingresa tu comando..."):
        if not api_key:
            st.error("⚠️ Acceso denegado: Falta API Key.")
            st.stop()
        
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        try:
            client = Groq(api_key=api_key)
            with st.chat_message("assistant", avatar="💠"):
                stream = client.chat.completions.create(
                    model=get_model_by_tier(st.session_state.user_tier),
                    messages=st.session_state.mensajes,
                    temperature=0.5,
                    max_tokens=1024,
                    stream=True
                )
                
                # Generador limpio
                def stream_gen():
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                            
                response = st.write_stream(stream_gen())
                
            st.session_state.mensajes.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error del sistema: {e}")
