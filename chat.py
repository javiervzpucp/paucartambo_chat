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

# Función para guardar en Vectara
def save_to_vectara(query, response, satisfaction, document_id="2560b95df098dda376512766f44af3e0"):
    """
    Guarda la respuesta marcada como satisfactoria o no satisfactoria en Vectara.

    Args:
        query (str): La consulta realizada por el usuario.
        response (str): La respuesta generada por el sistema.
        satisfaction (str): Indica si la respuesta fue "Satisfactoria" o "No satisfactoria".
        document_id (str): ID del documento en el corpus de Vectara para adjuntar respuestas.
    """
    try:
        vectara.add_texts(
            texts=[
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Query: {query}\n"
                f"Response: {response}\n"
                f"Satisfaction: {satisfaction}"
            ],
            document_id=document_id,  # Especificar el mismo ID de documento para adjuntar
        )
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

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
        st.session_state.query = query_str
        rag = vectara.as_chat(config)
        response = rag.invoke(query_str)
        st.session_state.response = response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Área de respuesta editable
st.write("**Respuesta (editable):**")
if st.session_state.response:
    st.session_state.response = st.text_area("Edita la respuesta antes de guardar:", value=st.session_state.response, height=150)

# Botones de retroalimentación
st.write("**¿Esta respuesta fue satisfactoria?**")
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Sí"):
        save_to_vectara(st.session_state.query, st.session_state.response, "Satisfactoria")
with col2:
    if st.button("👎 No"):
        save_to_vectara(st.session_state.query, st.session_state.response, "No satisfactoria")
