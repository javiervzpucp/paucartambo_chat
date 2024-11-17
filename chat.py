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

# Inicializar el historial de consultas del usuario
if "user_history" not in st.session_state:
    st.session_state.user_history = []

# Función para generar preguntas sugeridas dinámicas
def generar_preguntas_sugeridas(historial):
    if not historial:
        # Preguntas predeterminadas si no hay historial
        return [
            "¿Qué danzas se presentan en honor a la Mamacha Carmen?",
            "¿Cuál es el origen de las devociones marianas en Paucartambo?",
            "¿Qué papeles tienen los diferentes grupos de danza en la festividad?",
            "¿Cómo se celebra la festividad de la Virgen del Carmen?",
            "¿Cuál es el significado de las vestimentas en las danzas?",
        ]
    
    # Generar recomendaciones basadas en el historial
    recomendaciones = []
    for consulta in historial:
        response = vectara.as_chat(config).invoke(
            f"Basándote en la pregunta '{consulta}', sugiere una consulta relacionada."
        )
        preguntas = response.get("answer", "").split("\n")
        recomendaciones.extend(preguntas)

    # Filtrar duplicados y devolver las preguntas sugeridas
    return list(set(recomendaciones))[:5]

# Generar preguntas sugeridas dinámicamente
preguntas_sugeridas = generar_preguntas_sugeridas(st.session_state.user_history)

# Título de la aplicación
st.title("Prototipo de chat sobre las Devociones Marianas de Paucartambo")

# Imagen de portada
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption="Virgen del Carmen de Paucartambo",
    use_container_width=True,
)

# Mostrar preguntas sugeridas
st.write("**Preguntas sugeridas dinámicas:**")
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        st.session_state.query = pregunta

# Entrada personalizada
query_str = st.text_input(
    "Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:",
    value=st.session_state.query if "query" in st.session_state else "",
)

# Botón para obtener respuesta
if st.button("Responder"):
    if query_str.strip():
        with st.spinner("Generando respuesta..."):
            st.session_state.query = query_str
            rag = vectara.as_chat(config)
            response = rag.invoke(query_str)
            st.session_state.response = response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
            st.session_state.user_history.append(query_str)  # Agregar al historial del usuario
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Mostrar la respuesta
st.write("**Respuesta:**")
if "response" in st.session_state:
    st.text_area(
        "Edita la respuesta antes de guardar:",
        value=st.session_state.response,
        height=150,
    )

# Guardar respuesta marcada como satisfactoria
def guardar_respuesta(query, response, satisfaction):
    # Aquí podrías integrarlo con tu sistema actual de almacenamiento (como Vectara)
    st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada correctamente!")

# Botones de retroalimentación
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Sí"):
        guardar_respuesta(st.session_state.query, st.session_state.response, "Satisfactoria")
with col2:
    if st.button("👎 No"):
        guardar_respuesta(st.session_state.query, st.session_state.response, "No satisfactoria")
