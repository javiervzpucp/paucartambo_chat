# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024

@author: jveraz
"""

import streamlit as st
import pandas as pd
import requests
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

# Public Google Sheets URLs
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1jGwtHJNbIVCR4JwTRR_-yK4Yl_Csi6W7BiA87mQBVK4/gviz/tq?tqx=out:csv"
GOOGLE_SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1jGwtHJNbIVCR4JwTRR_-yK4Yl_Csi6W7BiA87mQBVK4/edit"


# Load data from Google Sheets
@st.cache
def load_data():
    try:
        data = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        return data
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame(columns=["timestamp", "query", "response"])

# Append new data to Google Sheets (Save locally)
def append_to_google_sheet(new_row):
    try:
        # Load existing data
        data = load_data()

        # Append the new row
        updated_data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

        # Save updated data locally (overwrite old file)
        updated_data.to_csv("updated_sheet.csv", index=False)

        # Provide instructions to manually upload the updated CSV
        st.info("The updated responses have been saved locally as 'updated_sheet.csv'.")
        st.info(f"Please upload this file to the Google Sheet via {GOOGLE_SHEET_EDIT_URL}.")
    except Exception as e:
        st.error(f"Error updating Google Sheets: {e}")

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

# Dropdown to select a suggested question
st.write("**Preguntas sugeridas**")
selected_question = st.selectbox("Selecciona una pregunta sugerida:", preguntas_sugeridas)

# Text input for a custom query
query_str = st.text_input(
    "Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:",
    value=selected_question,
)

# Query Vectara for a response
rag = vectara.as_chat(config)
response = rag.invoke(query_str)

# Display the generated response
st.write("**Respuesta:**")
st.write(response.get('answer', "Lo siento, no tengo suficiente información para responder a tu pregunta."))

# Display saved responses from Google Sheets
st.write("**Respuestas guardadas:**")
data = load_data()
if not data.empty:
    st.write(data)
else:
    st.info("No hay respuestas guardadas aún.")

# Collect user feedback
if st.button("Guardar esta respuesta como satisfactoria"):
    new_row = {
        "timestamp": datetime.now().isoformat(),
        "query": query_str,
        "response": response.get('answer', "No response available"),
    }
    append_to_google_sheet(new_row)
