# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024

@author: jveraz
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from langchain_community.vectorstores.vectara import (
    RerankConfig,
    SummaryConfig,
    VectaraQueryConfig,
)
from datetime import datetime

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

# Function to generate suggested questions
def generate_suggested_questions(query):
    """
    Use Vectara to generate suggested questions based on data.
    
    Args:
        query (str): A query to prompt Vectara for related questions.

    Returns:
        list: A list of suggested questions.
    """
    rag = vectara.as_chat(config)
    response = rag.invoke(query)
    suggestions = []
    if response and "answer" in response:
        suggestions = response["answer"].split("\n")  # Split lines to extract suggestions
    return suggestions[:5]  # Return up to 5 suggestions

# Title
st.markdown("<h1 style='font-size: 36px;'>Prototipo de chat sobre las Devociones Marianas de Paucartambo</h1>", unsafe_allow_html=True)

# Display an image below the title
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption="Virgen del Carmen de Paucartambo",
    use_container_width=True,
)

# Generate suggested questions
st.write("**Preguntas sugeridas:**")
default_query = "¿Qué preguntas suelen hacerse sobre las devociones marianas y las danzas de Paucartambo?"
suggested_questions = generate_suggested_questions(default_query)

if not suggested_questions:
    st.write("No se generaron preguntas sugeridas en este momento. Intenta formular una pregunta.")

# Show suggested questions as buttons
selected_question = None
if suggested_questions:
    for pregunta in suggested_questions:
        if st.button(pregunta):
            selected_question = pregunta

# Input for custom questions
query_str = st.text_input(
    "Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:",
    value=selected_question if selected_question else "",
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

# Editable response
st.write("**Respuesta (editable):**")
if "response" not in st.session_state:
    st.session_state.response = ""

st.session_state.response = st.text_area(
    "Edita la respuesta si es necesario:",
    value=st.session_state.response,
    height=150
)

# Feedback buttons
st.write("**¿Esta respuesta fue satisfactoria?**")
col1, col2 = st.columns(2)

with col1:
    if st.button("👍 Sí"):
        vectara.add_texts(
            texts=[
                f"Query: {st.session_state.query}\nResponse: {st.session_state.response}\nSatisfaction: Satisfactoria"
            ],
            document_id="satisfactory_responses_doc"
        )
        st.success("¡Respuesta marcada como 'Satisfactoria' y guardada en Vectara!")

with col2:
    if st.button("👎 No"):
        vectara.add_texts(
            texts=[
                f"Query: {st.session_state.query}\nResponse: {st.session_state.response}\nSatisfaction: No satisfactoria"
            ],
            document_id="satisfactory_responses_doc"
        )
        st.success("¡Respuesta marcada como 'No satisfactoria' y guardada en Vectara!")
