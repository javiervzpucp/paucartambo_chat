# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from langchain_community.vectorstores.vectara import VectaraQueryConfig
from dotenv import load_dotenv
from datetime import datetime
import os

# Cargar las variables de entorno desde el archivo secrets.toml
load_dotenv()

# Configuración de credenciales
vectara_customer_id = st.secrets["vectara"]["CUSTOMER_ID"]
vectara_corpus_id = st.secrets["vectara"]["CORPUS_ID"]
vectara_api_key = st.secrets["vectara"]["API_KEY"]

# Validar credenciales
if not vectara_customer_id or not vectara_corpus_id or not vectara_api_key:
    raise ValueError("Falta información de Vectara. Configúrala en el archivo secrets.toml")

# Inicializar cliente de Vectara
vectara = Vectara(
    vectara_customer_id=vectara_customer_id,
    vectara_corpus_id=vectara_corpus_id,
    vectara_api_key=vectara_api_key,
)

# Configuración para consultas
config = VectaraQueryConfig(
    k=10,  # Número de resultados
    lambda_val=0.0  # Parámetro para ajustar entre relevancia y contexto
)
rag = vectara.as_chat(config)

# Función para guardar respuestas satisfactorias
def save_to_vectara(query, response, satisfaction, document_id="2560b95df098dda376512766f44af3e0"):
    try:
        vectara.add_texts(
            texts=[
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Query: {query}\n"
                f"Response: {response}\n"
                f"Satisfaction: {satisfaction}"
            ],
            document_id=document_id
        )
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Interfaz de Streamlit
st.title("Prototipo de Chat sobre las Devociones Marianas de Paucartambo")

# Mostrar imagen
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

# Mostrar preguntas sugeridas como botones
st.write("**Preguntas sugeridas**")
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        st.session_state.query = pregunta  # Actualiza el estado de la consulta
        st.session_state.response = None  # Reinicia la respuesta previa

# Asegurar que `st.session_state.query` está inicializado
if "query" not in st.session_state:
    st.session_state.query = ""

# Entrada personalizada
query = st.text_input("Haz una pregunta relacionada con las Devociones Marianas de Paucartambo:", value=st.session_state.query)

# Procesar consulta
if st.button("Responder"):
    if query.strip():
        try:
            st.session_state.query = query  # Guarda la última consulta
            response = rag.invoke(query)
            st.session_state.response = response["answer"]

            # Mostrar la respuesta generada
            st.write("**Última pregunta generada:**")
            st.write(f"Pregunta: {st.session_state['query']}")
            st.write(f"Respuesta: {st.session_state['response']}")

            # Listar documentos fuente sin duplicados
            st.write("**Documentos fuente:**")
            source_documents = list(set([doc["source"] for doc in response["results"]]))
            for doc in source_documents:
                st.write(doc)

        except Exception as e:
            st.error(f"Error al consultar Vectara: {e}")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Retroalimentación del usuario
if "response" in st.session_state and st.session_state.response:
    st.write("**¿Esta respuesta fue satisfactoria?**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Sí"):
            save_to_vectara(
                query=st.session_state["query"],
                response=st.session_state["response"],
                satisfaction="Satisfactoria"
            )

    with col2:
        if st.button("👎 No"):
            save_to_vectara(
                query=st.session_state["query"],
                response=st.session_state["response"],
                satisfaction="No satisfactoria"
            )
