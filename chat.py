# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024

@author: jveraz
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from langchain_community.vectorstores import Vectara
from langchain_community.vectorstores.vectara import (
    RerankConfig,
    SummaryConfig,
    VectaraQueryConfig,
)

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

# Google Sheets URL
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1jGwtHJNbIVCR4JwTRR_-yK4Yl_Csi6W7BiA87mQBVK4/gviz/tq?tqx=out:csv"
GOOGLE_SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1jGwtHJNbIVCR4JwTRR_-yK4Yl_Csi6W7BiA87mQBVK4/edit"

# Load data from Google Sheets
@st.cache_data
def load_data():
    try:
        data = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        return data
    except Exception as e:
        return pd.DataFrame(columns=["timestamp", "query", "response"])

# Append satisfactory responses to a local CSV for manual upload
def append_to_csv(new_row):
    try:
        # Load existing data
        try:
            data = pd.read_csv("satisfactory_responses.csv")
        except FileNotFoundError:
            data = pd.DataFrame(columns=["timestamp", "query", "response"])

        # Append the new row
        updated_data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

        # Save updated data locally
        updated_data.to_csv("satisfactory_responses.csv", index=False)

        # Provide instructions for manual upload
        st.info("Responses saved locally in 'satisfactory_responses.csv'.")
        st.info(f"Please upload this file to the Google Sheet: {GOOGLE_SHEET_EDIT_URL}")
    except Exception as e:
        st.error(f"Error saving response: {e}")

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
        selected_question = pregunta

# Text input for a custom query
query_str = st.text_input(
    "Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:",
    value=selected_question if selected_question else "",
)

# Query Vectara for a response
rag = vectara.as_chat(config)
response = rag.invoke(query_str)

# Display the generated response
st.write("**Respuesta:**")
st.write(response.get('answer', "Lo siento, no tengo suficiente información para responder a tu pregunta."))

# Display saved responses from Google Sheets
st.write("**Respuestas satisfactorias guardadas:**")
data = load_data()
if not data.empty:
    st.write(data)
else:
    st.info("No hay respuestas satisfactorias guardadas aún. ¡Sé el primero en enviar una!")

# Collect user feedback for satisfactory response
if st.button("Guardar esta respuesta como satisfactoria"):
    new_row = {
        "timestamp": datetime.now().isoformat(),  # Timestamp
        "query": query_str,                      # User query
        "response": response.get('answer', "No response available"),  # Response
    }
    append_to_csv(new_row)
    st.success("¡Respuesta satisfactoria guardada!")
