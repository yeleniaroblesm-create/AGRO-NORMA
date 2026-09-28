import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AGRO NORMA - CAAE", page_icon="🌾", layout="centered")

# --- CONTROL DE ACCESO INSTITUCIONAL (CAAE) ---
def verificar_password():
    """Función para solicitar contraseña institucional"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔒 Acceso Restringido - AGRO NORMA")
        st.markdown("### Sistema exclusivo para personal de CAAE")
        
        password_ingresada = st.text_input("Ingrese la contraseña institucional:", type="password")
        
        if st.button("Ingresar"):
            if password_ingresada == "caae2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Acceso denegado.")
        return False
    return True

if not verificar_password():
    st.stop()

# --- APLICACIÓN PRINCIPAL ---
st.title("🌾 AGRO NORMA")
st.markdown("### Asistente técnico especializado en normativas agrícolas (CAAE)")

# Configuración de la API Key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Ingresa tu Google GenAI API Key:", type="password")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error al inicializar el cliente: {e}")

    # CARGA AUTOMÁTICA DE LOS DOCUMENTOS OFICIALES DESDE EL REPOSITORIO
    nombres_pdfs = [
        "GG_CoC_doc 1.pdf", 
        "GG_CoC_doc 2.pdf", 
        "GG_IFA_doc1.pdf", 
        "GG_IFA_doc2.pdf", 
        "GG_IFA_doc3.pdf", 
        "NOE_doc1.pdf"
    ]
    
    documentos_bytes = []
    for pdf in nombres_pdfs:
        if os.path.exists(pdf):
            with open(pdf, "rb") as f:
                documentos_bytes.append(f.read())

    st.sidebar.success(f"🔒 Sistema conectado: {len(documentos_bytes)} normativas oficiales cargadas de forma permanente.")

    # Historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Escribe tu consulta sobre la normativa..."):
        if not documentos_bytes:
            st.error("⚠️ No se encontraron los archivos PDF en el repositorio. Verifique los nombres.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analizando normativa oficial..."):
                    try:
                        contents = []
                        for b in documentos_bytes:
                            contents.append(
                                types.Part.from_bytes(
                                    data=b,
                                    mime_type="application/pdf",
                                )
                            )
                        
                        contents.append(prompt)

                        system_instruction = (
                            "Actúa como AGRO NORMA, asistente técnico experto en normativas agrícolas para CAAE. "
                            "Tu única fuente de verdad son de forma exclusiva los documentos PDF institucionales adjuntos. "
                            "REGLAS ESTRICTAS:\n"
                            "1. PROHIBIDO ALUCINAR O INVENTAR: No uses conocimientos externos ni suposiciones.\n"
                            "2. RESPUESTA ANTE VACÍOS: Si la información exacta no se encuentra en el texto de los documentos adjuntos, "
                            "responde textualmente y sin rodeos: 'La información solicitada no se encuentra disponible en la normativa oficial cargada'.\n"
                            "3. RESTRICCIÓN DE ENLACES: No generes URLs por iniciativa propia. Solo puedes incluir un enlace si está explícitamente "
                            "escrito en el documento fuente, limitado estrictamente a los dominios agrocalidad.gob.ec o globalgap.org."
                        )

                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.0
                            )
                        )
                        
                        bot_response = response.text
                        st.markdown(bot_response)
                        st.session_state.messages.append({"role": "assistant", "content": bot_response})

                    except Exception as e:
                        st.error(f"Ocurrió un error al procesar la solicitud: {e}")
else:
    st.info("💡 Por favor ingresa tu clave API para habilitar la aplicación.")
