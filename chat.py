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
from translate import Translator

# Initialize session state for language
if "language" not in st.session_state:
    st.session_state.language = "Español"
if "query" not in st.session_state:
    st.session_state.query = ""
if "response" not in st.session_state:
    st.session_state.response = ""

# Translation function
def translate_text(text, target_language):
    try:
        translator = Translator(to_lang=target_language)
        return translator.translate(text)
    except Exception:
        return text  # Return the original text if translation fails

# Language mapping
language_map = {
    "Español": "es",
    "English": "en",
    "Quechua": "qu",
}

# Sidebar for language selection
st.sidebar.title("Configuración")
selected_language = st.sidebar.selectbox(
    "Seleccione un idioma / Choose a language / Rimanapayay hina simi suyay",
    list(language_map.keys())
)

# Update session state language
st.session_state.language = selected_language
selected_language_code = language_map[selected_language]

# Dynamic translation
def dynamic_translation(text):
    return translate_text(text, selected_language_code)

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

# Title
st.markdown(f"### {dynamic_translation('Prototipo de chat sobre las Devociones Marianas de Paucartambo')}")

# Display an image below the title
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption=dynamic_translation("Virgen del Carmen de Paucartambo"),
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

# Translate suggested questions to the selected language
preguntas_sugeridas_translated = [dynamic_translation(p) for p in preguntas_sugeridas]

# Show suggested questions as buttons
st.write(f"**{dynamic_translation('Preguntas sugeridas')}**")
selected_question = None
for pregunta in preguntas_sugeridas_translated:
    if st.button(pregunta):
        st.session_state.query = pregunta  # Update session state query

# Input for custom questions
query_str = st.text_input(
    dynamic_translation("Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:"),
    value=st.session_state.query,
)

# "Responder" button to fetch response
if st.button(dynamic_translation("Responder")):
    if query_str.strip():
        st.session_state.query = query_str
        rag = vectara.as_chat(config)
        response = rag.invoke(query_str)
        translated_response = dynamic_translation(
            response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
        )
        st.session_state.response = translated_response
    else:
        st.warning(dynamic_translation("Por favor, ingresa una pregunta válida."))

# Editable response area
st.write(f"**{dynamic_translation('Respuesta (editable):')}**")
if st.session_state.response:
    st.session_state.response = st.text_area(
        dynamic_translation("Edita la respuesta antes de guardar:"),
        value=st.session_state.response,
        height=150,
    )

# Save satisfactory responses in Vectara
def save_to_vectara(query, response, satisfaction, document_id="2560b95df098dda376512766f44af3e0"):
    try:
        vectara.add_texts(
            texts=[
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Query: {query}\n"
                f"Response: {response}\n"
                f"Satisfaction: {satisfaction}"
            ],
            document_id=document_id,  # Specify the same document ID for appending
        )
        st.success(dynamic_translation(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!"))
    except Exception as e:
        st.error(dynamic_translation(f"Error al guardar la respuesta en Vectara: {e}"))

# Thumbs-up and Thumbs-down buttons for feedback
st.write(f"**{dynamic_translation('¿Esta respuesta fue satisfactoria?')}**")
col1, col2 = st.columns(2)

with col1:
    if st.button("👍 " + dynamic_translation("Sí")):
        save_to_vectara(st.session_state.query, st.session_state.response, "Satisfactoria")

with col2:
    if st.button("👎 " + dynamic_translation("No")):
        save_to_vectara(st.session_state.query, st.session_state.response, "No satisfactoria")
