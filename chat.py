# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from docx import Document
from io import BytesIO
from langchain_community.vectorstores import Vectara
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de credenciales
openai_api_key = st.secrets['openai']["OPENAI_API_KEY"]
vectara_customer_id = 2620549959
vectara_corpus_id = 2
vectara_api_key = "zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ"

# Inicializar cliente de Vectara
vectara = Vectara(
    vectara_customer_id=str(vectara_customer_id),
    vectara_corpus_id=vectara_corpus_id,
    vectara_api_key=vectara_api_key,
)

# Configuración de Streamlit
st.title("Prototipo de Chat sobre Devociones Marianas de Paucartambo")

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
    try:
        rag = vectara.as_chat()
        response = rag.invoke(query)
        return response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
    except Exception as e:
        st.error(f"Error al consultar Vectara: {e}")
        return "Lo siento, hubo un error al generar la respuesta."

# Generar respuesta
response = ""
if st.button("Responder"):
    if query.strip():
        response = fetch_vectara_response(query)
        st.write("**Respuesta generada:**")
        st.write(response)
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Exportar respuesta como .docx
if response:
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

    # Botón para descargar el archivo Word
    if st.button("Exportar respuesta a Word"):
        doc_file = export_to_doc(query, response)
        st.download_button(
            label="Descargar respuesta en formato Word",
            data=doc_file,
            file_name="respuesta_devociones.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # Compartir en redes sociales
    st.write("**Compartir esta respuesta en redes sociales:**")

    # Crear enlaces para compartir
    base_url = "https://twitter.com/intent/tweet"
    text = quote(f"Pregunta: {query}\nRespuesta: {response[:200]}...")
    twitter_url = f"{base_url}?text={text}"

    # Enlace para Twitter
    st.markdown(
        f"[Compartir en Twitter](https://twitter.com/intent/tweet?text={text})",
        unsafe_allow_html=True
    )

    # Enlace para LinkedIn
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(text)}"
    st.markdown(
        f"[Compartir en LinkedIn]({linkedin_url})",
        unsafe_allow_html=True
    )

    # Enlace para Facebook
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={quote(text)}"
    st.markdown(
        f"[Compartir en Facebook]({facebook_url})",
        unsafe_allow_html=True
    )
