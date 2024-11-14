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

# Configuración de Vectara
vectara = Vectara(
                vectara_customer_id="2620549959",
                vectara_corpus_id=2,
                vectara_api_key="zqt_nDJrRzuEwpSstPngTiTio43sQzykyJ1x6PebAQ"
            )

# Configuraciones adicionales de Vectara
summary_config = SummaryConfig(is_enabled=True, max_results=5, response_lang="spa")
rerank_config = RerankConfig(reranker="mmr", rerank_k=50, mmr_diversity_bias=0.1)
config = VectaraQueryConfig(
    k=10, lambda_val=0.0, rerank_config=rerank_config, summary_config=summary_config
)

# Título grande
st.markdown("<h1 style='font-size: 36px;'>Prototipo de chat sobre las Devociones Marianas de Paucartambo</h1>", unsafe_allow_html=True)

# Mostrar imagen debajo del título
st.image("https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png", caption="Virgen del Carmen de Paucartambo", use_container_width=True)

# Lista de preguntas sugeridas
preguntas_sugeridas = [
    "¿Qué danzas se presentan en honor a la Mamacha Carmen?",
    "¿Cuál es el origen de las devociones marianas en Paucartambo?",
    "¿Qué papeles tienen los diferentes grupos de danza en la festividad?",
    "¿Cómo se celebra la festividad de la Virgen del Carmen?",
    "¿Cuál es el significado de las vestimentas en las danzas?",
]

# Pregunta inicial predeterminada
pregunta_inicial = "¿Qué danzas se presentan en honor a la Mamacha Carmen?"

# Variable para almacenar la pregunta seleccionada
selected_question = pregunta_inicial

# Mostrar preguntas sugeridas como botones tipo cajita
st.write("**Preguntas sugeridas**")
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        selected_question = pregunta  # Almacenar la pregunta seleccionada

# Campo de entrada para consulta personalizada, prellenado con la pregunta seleccionada si existe
query_str = st.text_input(
    "Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo. "
    "En lo posible, te sugerimos formular preguntas específicas.",
    value=selected_question
)

# Llamada al modelo con la consulta seleccionada o personalizada
rag = vectara.as_chat(config)
resp = rag.invoke(query_str)

# Mostrar la respuesta
st.write("**Respuesta**")
st.write(resp['answer'])
