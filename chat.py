# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024

@author: jveraz
"""

import streamlit as st
from datetime import datetime
from langchain_community.vectorstores import Vectara
from langchain_community.vectorstores.vectara import (
    RerankConfig,
    SummaryConfig,
    VectaraQueryConfig,
)
from io import BytesIO
from docx import Document  # For creating Word documents

# Vectara Configuration
vectara = Vectara(
    vectara_customer_id="2620549959",
    vectara_corpus_id=2,
    vectara_api_key="zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ",
)

summary_config = SummaryConfig(is_enabled=True, max_results=5, response_lang="spa")
rerank_config = RerankConfig(reranker="mmr", rerank_k=50, mmr_diversity_bias=0.1)
config = VectaraQueryConfig(
    k=10, lambda_val=0.0, rerank_config=rerank_config, summary_config=summary_config
)

# Initialize session state for query and response persistence
if "query" not in st.session_state:
    st.session_state.query = ""
if "response" not in st.session_state:
    st.session_state.response = ""

# Store satisfactory responses in Vectara under a single document
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
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara bajo el documento '{document_id}'!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Function to create and download a Word document
def create_word_doc(query, response):
    doc = Document()
    doc.add_heading("Respuesta a la consulta", level=1)
    doc.add_paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph(f"Consulta: {query}")
    doc.add_heading("Respuesta:", level=2)
    doc.add_paragraph(response)
    
    # Save to BytesIO for download
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Title
st.markdown("<h1 style='font-size: 36px;'>Prototipo de chat sobre las Devociones Marianas de Paucartambo</h1>", unsafe_allow_html=True)

# Display an image below the title
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption="Virgen del Carmen de Paucartambo",
    use_container_width=True,
)

# Suggested questions
preguntas_sugeridas = [
    "¿Qué danzas se presentan en honor a la Mamacha Carmen?",
    "¿Cuál es el origen de las devociones marianas en Paucartambo?",
    "¿Qué papeles tienen los diferentes grupos de danza en la festividad?",
    "¿Cómo se celebra la festividad de la Virgen del Carmen?",
    "¿Cuál es el significado de las vestimentas en las danzas?",
]

# Show suggested questions as buttons
st.write("**Preguntas sugeridas**")
selected_question = None
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        st.session_state.query = pregunta  # Update session state query

# Input for custom questions
query_str = st.text_input(
    "Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:",
    value=st.session_state.query,
)

# "Responder" button to fetch response
if st.button("Responder"):
    if query_str.strip():
        st.session_state.query = query_str
        rag = vectara.as_chat(config)
        response = rag.invoke(query_str)
        st.session_state.response = response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Editable response area
st.write("**Respuesta (editable):**")
if st.session_state.response:
    st.session_state.response = st.text_area(
        "Edita la respuesta antes de guardar:",
        value=st.session_state.response,
        height=150,
    )

# Download Word document
if st.session_state.response:
    doc_buffer = create_word_doc(st.session_state.query, st.session_state.response)
    st.download_button(
        label="Descargar respuesta como Word",
        data=doc_buffer,
        file_name="respuesta.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

# Thumbs-up and Thumbs-down buttons for feedback
st.write("**¿Esta respuesta fue satisfactoria?**")
col1, col2 = st.columns(2)

with col1:
    if st.button("👍 Sí"):
        save_to_vectara(st.session_state.query, st.session_state.response, "Satisfactoria")

with col2:
    if st.button("👎 No"):
        save_to_vectara(st.session_state.query, st.session_state.response, "No satisfactoria")
