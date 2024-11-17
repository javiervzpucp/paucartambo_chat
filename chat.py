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

# Inicialización del estado de la sesión
if "query" not in st.session_state:
    st.session_state.query = ""
if "response" not in st.session_state:
    st.session_state.response = ""

# Configuración de Vectara
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

# Título
st.markdown("### Prototipo de chat sobre las Devociones Marianas de Paucartambo")

# Imagen
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

# Mostrar preguntas sugeridas
st.write("**Preguntas sugeridas**")
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        st.session_state.query = pregunta

# Entrada personalizada
query_str = st.text_input("Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:", value=st.session_state.query)

# Botón de respuesta
if st.button("Responder"):
    if query_str.strip():
        rag = vectara.as_chat(config)
        response = rag.invoke(query_str)
        st.session_state.response = response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Área de respuesta editable
st.write("**Respuesta (editable):**")
st.text_area("Edita la respuesta antes de guardar:", value=st.session_state.response)

# Botones de retroalimentación
st.write("**¿Esta respuesta fue satisfactoria?**")
col1, col2 = st.columns(2)
with col1:
    st.button("👍 Sí")
with col2:
    st.button("👎 No")
