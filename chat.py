# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de credenciales
vectara_customer_id = 2620549959
vectara_corpus_id = 2
vectara_api_key = "zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ"

# Validar que todas las variables se hayan cargado correctamente
if not vectara_customer_id or not vectara_corpus_id or not vectara_api_key:
    raise ValueError("Falta información de Vectara. Configúrala en el archivo .env")

# Configuración de Vectara
vectara = Vectara(
    vectara_customer_id=str(vectara_customer_id),
    vectara_corpus_id=vectara_corpus_id,
    vectara_api_key=vectara_api_key,
)

# Función para realizar consultas a Vectara
def fetch_vectara_documents(query):
    """
    Realiza una consulta a la API de Vectara para obtener documentos relacionados.
    """
    try:
        response = vectara.query(query)
        results = response.get("documents", [])
        if results:
            return results  # Lista de documentos relacionados
        else:
            return []
    except Exception as e:
        raise Exception(f"Error al consultar Vectara: {e}")

# Función para mostrar los resultados obtenidos de Vectara
def format_vectara_response(documents):
    """
    Formatea los documentos obtenidos de Vectara en un texto amigable.
    """
    formatted_response = []
    for i, doc in enumerate(documents):
        text = doc.get("text", "Sin texto disponible")
        source = doc.get("source", "Fuente desconocida")
        score = doc.get("score", "Sin puntuación")
        formatted_response.append(f"Resultado {i+1}:\nTexto: {text}\nFuente: {source}\nPuntuación: {score}\n")
    return "\n".join(formatted_response)

# Función para guardar respuestas útiles en Vectara
def save_to_vectara(query, response):
    """
    Guarda la consulta y respuesta útil en un documento de Vectara.
    """
    try:
        timestamp = datetime.now().isoformat()
        vectara.add_texts(
            texts=[f"Timestamp: {timestamp}\nQuery: {query}\nResponse: {response}"],
            document_id="useful_responses"  # ID del documento donde se guardarán las respuestas útiles
        )
        st.success("¡Respuesta marcada como útil y guardada en Vectara!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Interfaz de Streamlit
st.title("Prototipo de Chat sobre Devociones Marianas de Paucartambo")

# Mostrar imagen principal
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
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        st.session_state.query = pregunta

# Entrada del usuario
query = st.text_input("Haz una pregunta relacionada con las Devociones Marianas de Paucartambo:", value=st.session_state.get("query", ""))

# Botón para obtener respuestas
if st.button("Responder"):
    if query.strip():
        try:
            # Consultar documentos relevantes en Vectara
            documents = fetch_vectara_documents(query)
            if documents:
                # Formatear y mostrar los resultados
                formatted_response = format_vectara_response(documents)
                st.write("**Resultados obtenidos de Vectara:**")
                st.text(formatted_response)
                st.session_state["response"] = formatted_response
            else:
                st.warning("No se encontraron documentos relevantes en Vectara.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Mostrar respuesta generada si existe
if "response" in st.session_state:
    st.write("**Respuesta generada:**")
    st.text(st.session_state["response"])

# Retroalimentación del usuario
st.write("**¿Esta respuesta fue útil?**")
col1, col2 = st.columns(2)

with col1:
    if st.button("👍 Sí"):
        try:
            save_to_vectara(query, st.session_state["response"])
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("👎 No"):
        st.warning("Gracias por tu retroalimentación. Trabajaremos para mejorar.")
