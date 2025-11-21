import streamlit as st
from groq import Groq
import pandas as pd
import PyPDF2

# --- Configuración de la Página ---
st.set_page_config(page_title="Analista IA Pro", page_icon="🕵️", layout="wide")

st.title("🕵️ Analista de Documentos IA")
st.markdown("Sube un PDF o Excel y haz preguntas sobre su contenido.")

# --- Barra Lateral ---
with st.sidebar:
    st.header("1. Configuración")
    
    # Lógica inteligente para la API Key:
    # 1. Intenta leerla de los "Secretos" de Streamlit Cloud
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("✅ API Key cargada desde el sistema")
    else:
        # 2. Si no hay secreto (estás en local), pídela manual
        api_key = st.text_input("Tu API Key de Groq:", type="password")

    st.header("2. Tus Documentos")
    # ¡ESTA ES LA LÍNEA QUE FALTABA!
    uploaded_file = st.file_uploader("Sube un archivo", type=["pdf", "xlsx", "xls", "csv"])
    
    if st.button("Limpiar conversación"):
        st.session_state.mensajes = []
        st.rerun()

# --- Funciones ---
def procesar_texto(archivo):
    texto = ""
    try:
        if archivo.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(archivo)
            for page in reader.pages:
                texto += page.extract_text() or ""
        elif archivo.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(archivo)
            texto = df.to_string()
        elif archivo.name.endswith('.csv'):
            df = pd.read_csv(archivo)
            texto = df.to_string()
        return texto
    except Exception as e:
        return f"Error leyendo archivo: {e}"

def generar_respuesta_limpia(chat_completion):
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# --- Estado de la Sesión ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- Lógica Principal ---
# Verificamos que uploaded_file no sea None (usuario subió algo)
if uploaded_file is not None and api_key:
    file_key = f"processed_{uploaded_file.name}"
    if file_key not in st.session_state:
        with st.spinner("Analizando documento..."):
            contenido_doc = procesar_texto(uploaded_file)
            contenido_doc = contenido_doc[:30000] 
            
            system_prompt = f"""
            Actúa como un analista experto. El usuario te ha proporcionado un documento.
            Responde basándote SOLO en la siguiente información:
            
            --- DOCUMENTO ---
            {contenido_doc}
            --- FIN ---
            """
            st.session_state.mensajes = [{"role": "system", "content": system_prompt}]
            st.session_state[file_key] = True
            st.success("✅ Documento analizado.")

# --- Chat ---
for mensaje in st.session_state.mensajes:
    if mensaje["role"] != "system":
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

prompt = st.chat_input("Pregunta sobre el archivo...")

if prompt:
    if not api_key:
        st.warning("⚠️ Falta la API Key. Configúrala en los 'Secrets' o en la barra lateral.")
        st.stop()
        
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = Groq(api_key=api_key)
        
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.mensajes,
                temperature=0.3,
                max_tokens=1024,
                stream=True,
            )
            response = st.write_stream(generar_respuesta_limpia(stream))
            
        st.session_state.mensajes.append({"role": "assistant", "content": response})
        
    except Exception as e:
        st.error(f"Error: {e}")