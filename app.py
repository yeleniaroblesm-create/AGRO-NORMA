import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AGRO NORMA - CAAE", page_icon="🌾", layout="centered")

# --- ESTILO VISUAL / TONOS INSTITUCIONALES CAAE ---
st.markdown("""
    <style>
    /* Fondo con degradado en tonos verdes institucionales suaves */
    .stApp {
        background: linear-gradient(135deg, #eef5f0 0%, #d8ebd9 100%);
    }
    
    /* Estilo personalizado para resaltar los títulos */
    h1, h2, h3 {
        color: #1b4d2e !important;
    }
    
    /* Contenedor de la barra lateral con tono coordinado */
    [data-testid="stSidebar"] {
        background-color: #f4f8f4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROL DE ACCESO INSTITUCIONAL (CAAE) ---
def verificar_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔒 Acceso Restringido - AGRO NORMA (CAAE)")
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
st.title("🌾 AGRO NORMA - CAAE")
st.markdown("### Asistente técnico especializado en normativas agrícolas")

api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Ingresa tu Google GenAI API Key:", type="password")

if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error al inicializar el cliente: {e}")

    st.sidebar.success("🔒 Sistema conectado: Normativas oficiales de CAAE listas.")

    # Historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Escribe tu consulta sobre la normativa..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generando respuesta oficial de CAAE..."):
                try:
                    # BASE DE PREGUNTAS Y RESPUESTAS OFICIALES CAAE
                    preguntas_respuestas_frecuentes = """
                    [BASE DE PREGUNTAS Y RESPUESTAS INSTITUCIONALES CAAE]
                    1. Pregunta: ¿Cuál es la superficie máxima que la norma orgánica ecuatoriana determina para determinar un pequeño productor de banano?
                       Respuesta: 10 hectáreas en monocultivo y 20 hectáreas en sistema agroforestales.
                    
                    2. Pregunta: ¿Cuáles son las condiciones de uso del azufre en la norma orgánica ecuatoriana?
                       Respuesta: Producto de origen natural o industrial más o menos refinado Contenido mínimo en elementos nutrientes (porcentaje en masa): 98 % S (245 %: SO3) como fertilizante; y, Fungicida, acaricida, repelente.
                    
                    3. Pregunta: ¿Cuál es la superficie máxima que la norma orgánica de la Unión Europea determina para determinar un pequeño productor de banano?
                       Respuesta: Los documentos cargados no me permite dar una respuesta. He realizado una búsqueda en enlaces externos y la respuesta es ……..
                    
                    4. Pregunta: ¿Se puede certificar a un productor que produce y empaca banano bajo las normas IFA y CoC?
                       Respuesta: No. Los requisitos de trazabilidad y segregación para los productores que participan en la propiedad en la propiedad o en la producción paralela de productos certificados y no certificados ya están incluidos en el ámbito de la certificación IFA.
                    
                    5. Pregunta: ¿En CoC la empresa debe mantener registros precisos de compra y ventas?
                       Respuesta: Si. Es una obligación mayor.
                    
                    6. Pregunta: ¿In IFA GFS V6 el operador debe tener disponible los registros actualizados de todos los tratamientos químicos aplicados en el material de propagación propio?
                       Respuesta: Si. Es una obligación mayor.
                    
                    7. Pregunta: ¿Las auditorias de acompañamiento de la finca realizadas por el OC pueden ser consideradas aceptables para mantener la competencia de un auditor del OC de la finca globalgap opción 1?
                       Respuesta: Si.
                    
                    8. Pregunta: ¿En el ámbito de plantas qué incluye la manipulación del producto?
                       Respuesta: Incluye cualquier tipo de manipulación postcosecha de los productos, tal como almacenamiento, el tratamiento químico, el recorte, el lavado o cualquier manipulación donde el producto cosechado pueda tener contacto físico con otros materiales y sustancias.
                    """

                    prompt_completo = (
                        f"{preguntas_respuestas_frecuentes}\n\n"
                        f"Consulta del auditor/productor: {prompt}"
                    )

                    system_instruction = (
                        "Actúa como AGRO NORMA, asistente técnico experto en normativas agrícolas para CAAE. "
                        "Tu fuente de verdad son los documentos normativos institucionales y la base de preguntas y respuestas frecuentes definida en el texto. "
                        "REGLAS ESTRICTAS Y OBLIGATORIAS:\n"
                        "1. CUMPLE CON LAS PAUTAS: Si la pregunta coincide o se relaciona con las preguntas frecuentes institucionales, responde exactamente bajo esos criterios y respuestas exactas.\n"
                        "2. PROHIBIDO ALUCINAR O INVENTAR: No uses conocimientos externos ni suposiciones por fuera de las fuentes.\n"
                        "3. RESPUESTA ANTE VACÍOS: Si la información exacta no se encuentra en las bases oficiales, "
                        "responde textualmente y sin rodeos: 'La información solicitada no se encuentra disponible en la normativa oficial cargada'.\n"
                        "4. RESTRICCIÓN TOTAL DE ENLACES: No generes URLs ni enlaces por iniciativa propia bajo ninguna circunstancia. "
                        "Solo puedes incluir un enlace si está explícitamente autorizado, limitado estrictamente y sin excepciones a los dominios agrocalidad.gob.ec o globalgap.org."
                    )

                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt_completo,
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
