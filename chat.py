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

# Initialize translation function
def translate_text(text, target_language):
    translator = Translator(to_lang=target_language)
    return translator.translate(text)

# Initialize session state for language
if "language" not in st.session_state:
    st.session_state.language = "Español"  # Default language is Spanish

# Language selection at the beginning
st.markdown("### Seleccione un idioma / Choose a language / Rimanapayay hina simi suyay")
language = st.selectbox(
    "Idioma / Language / Simi",
    ["Español", "English", "Quechua"],
    index=["Español", "English", "Quechua"].index(st.session_state.language),
)

# Update session state language
if language != st.session_state.language:
    st.session_state.language = language
    st.experimental_rerun()  # Rerun the app to apply the language change

# Map the language choice to a language code for the Translator library
language_map = {
    "Español": "es",
    "English": "en",
    "Quechua": "qu",
}
selected_language_code = language_map[st.session_state.language]

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

# Title
st.markdown(translate_text("### Prototipo de chat sobre las Devociones Marianas de Paucartambo", selected_language_code))

# Display an image below the title
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption=translate_text("Virgen del Carmen de Paucartambo", selected_language_code),
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
preguntas_sugeridas_translated = [translate_text(p, selected_language_code) for p in preguntas_sugeridas]

# Show suggested questions as buttons
st.write(translate_text("**Preguntas sugeridas**", selected_language_code))
selected_question = None
for pregunta in preguntas_sugeridas_translated:
    if st.button(pregunta):
        st.session_state.query = pregunta  # Update session state query

# Input for custom questions
query_str = st.text_input(
    translate_text("Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:", selected_language_code),
    value=st.session_state.query,
)

# "Responder" button to fetch response
if st.button(translate_text("Responder", selected_language_code)):
    if query_str.strip():
        st.session_state.query = query_str
        rag = vectara.as_chat(config)
        response = rag.invoke(query_str)
        translated_response = translate_text(
            response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta."),
            selected_language_code,
        )
        st.session_state.response = translated_response
    else:
        st.warning(translate_text("Por favor, ingresa una pregunta válida.", selected_language_code))

# Editable response area
st.write(translate_text("**Respuesta (editable):**", selected_language_code))
if st.session_state.response:
    st.session_state.response = st.text_area(
        translate_text("Edita la respuesta antes de guardar:", selected_language_code),
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
        st.success(translate_text(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!", selected_language_code))
    except Exception as e:
        st.error(translate_text(f"Error al guardar la respuesta en Vectara: {e}", selected_language_code))

# Thumbs-up and Thumbs-down buttons for feedback
st.write(translate_text("**¿Esta respuesta fue satisfactoria?**", selected_language_code))
col1, col2 = st.columns(2)

with col1:
    if st.button("👍 " + translate_text("Sí", selected_language_code)):
        save_to_vectara(st.session_state.query, st.session_state.response, "Satisfactoria")

with col2:
    if st.button("👎 " + translate_text("No", selected_language_code)):
        save_to_vectara(st.session_state.query, st.session_state.response, "No satisfactoria")
