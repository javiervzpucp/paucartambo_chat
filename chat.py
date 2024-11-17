# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from docx import Document
from io import BytesIO
from urllib.parse import quote
from datetime import datetime
from langchain_community.vectorstores import Vectara
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Leer credenciales de Vectara
vectara_customer_id = os.getenv("CUSTOMER_ID")
vectara_corpus_id = os.getenv("CORPUS_ID")
vectara_api_key = os.getenv("API_KEY")

# Configuración de Vectara
vectara = Vectara(
    vectara_customer_id=str(vectara_customer_id),
    vectara_corpus_id=vectara_corpus_id,
    vectara_api_key=vectara_api_key,
)

# Configuración de la app
st.title("Prototipo de Chat sobre Devociones Marianas de Paucartambo")
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption="Virgen del Carmen de Paucartambo",
    use_container_width=True,
)

# Preguntas sugeridas
preguntas_sugeridas = [
    "¿Qué danzas se presentan en honor a la Mamacha Carmen?",
    "¿Cuál es el origen de las devociones marianas en Paucartambo?",
    "¿Qué papeles tienen los diferentes grupos de danza en la festividad?",
    "¿Cómo se celebra la festividad de la Virgen del Carmen?",
    "¿Cuál es el significado de las vestimentas en las danzas?",
]

st.write("**Preguntas sugeridas**")
selected_question = None
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        st.session_state.query = pregunta

# Input de consulta personalizada
query = st.text_input("Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:", value="")

# Función para generar respuestas utilizando Vectara
def fetch_vectara_response(query):
    """
    Genera respuestas utilizando Vectara.
    """
    try:
        rag = vectara.as_chat()
        response = rag.invoke(query)
        return response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
    except Exception as e:
        st.error(f"Error al consultar Vectara: {e}")
        return "Lo siento, hubo un error al generar la respuesta."

# Generar respuesta
if "response" not in st.session_state:
    st.session_state.response = ""

if st.button("Responder"):
    if query.strip():
        st.session_state.response = fetch_vectara_response(query)
        st.write("**Última respuesta generada:**")
        st.write(f"**Pregunta:** {query}")
        st.write(f"**Respuesta:** {st.session_state.response}")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Exportar respuesta como .docx
def export_to_doc(query, response):
    """
    Exporta la consulta y respuesta a un archivo .docx.
    """
    doc = Document()
    doc.add_heading("Respuesta Generada", level=1)
    doc.add_paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph(f"Pregunta: {query}")
    doc.add_paragraph(f"Respuesta: {response}")
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

if st.session_state.response:
    doc_file = export_to_doc(query, st.session_state.response)
    st.download_button(
        label="Descargar respuesta en formato Word",
        data=doc_file,
        file_name="respuesta_devociones.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Compartir en redes sociales
    st.write("**Compartir esta respuesta en redes sociales:**")

    # Crear enlaces para compartir
    text = quote(f"Pregunta: {query}\nRespuesta: {st.session_state.response[:200]}...")
    twitter_url = f"https://twitter.com/intent/tweet?text={text}"
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(text)}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={quote(text)}"

    # Enlaces a redes sociales
    st.markdown(
        f"[Compartir en Twitter]({twitter_url})", unsafe_allow_html=True
    )
    st.markdown(
        f"[Compartir en LinkedIn]({linkedin_url})", unsafe_allow_html=True
    )
    st.markdown(
        f"[Compartir en Facebook]({facebook_url})", unsafe_allow_html=True
    )
