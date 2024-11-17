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

# Inicializar el historial y preguntas dinámicas
if "user_history" not in st.session_state:
    st.session_state.user_history = []
if "dynamic_questions" not in st.session_state:
    st.session_state.dynamic_questions = []

# Función para generar preguntas dinámicas basadas en el historial
def generar_preguntas_dinamicas(historial, n=3):
    """Genera preguntas dinámicas en base al historial del usuario."""
    recomendaciones = []
    for consulta in historial:
        response = vectara.as_chat(config).invoke(
            f"Basándote en la pregunta '{consulta}', sugiere consultas relacionadas."
        )
        preguntas = response.get("answer", "").split("\n")
        recomendaciones.extend(preguntas)

    # Filtrar duplicados, evitar preguntas vacías y devolver N preguntas
    preguntas_unicas = list(set([p for p in recomendaciones if p.strip()]))
    return preguntas_unicas[:n]

# Actualizar preguntas dinámicas si no hay suficientes
if len(st.session_state.dynamic_questions) < 3:
    nuevas_preguntas = generar_preguntas_dinamicas(st.session_state.user_history, n=3 - len(st.session_state.dynamic_questions))
    st.session_state.dynamic_questions.extend(nuevas_preguntas)

# Título de la aplicación
st.title("Prototipo de chat sobre las Devociones Marianas de Paucartambo")

# Imagen de portada
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption="Virgen del Carmen de Paucartambo",
    use_container_width=True,
)

# Preguntas dinámicas
st.write("**Preguntas sugeridas dinámicas:**")
nuevas_preguntas = []
for pregunta in st.session_state.dynamic_questions:
    if st.button(pregunta):
        st.session_state.query = pregunta
        st.session_state.user_history.append(pregunta)  # Añadir al historial
        nuevas_preguntas = generar_preguntas_dinamicas([pregunta], n=1)  # Generar una nueva pregunta para reemplazarla
        st.session_state.dynamic_questions.remove(pregunta)
        st.session_state.dynamic_questions.extend(nuevas_preguntas)
        break  # Salir del loop tras procesar el clic

# Input para preguntas personalizadas
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
    st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada correctamente!")

# Botones de retroalimentación
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Sí"):
        guardar_respuesta(st.session_state.query, st.session_state.response, "Satisfactoria")
with col2:
    if st.button("👎 No"):
        guardar_respuesta(st.session_state.query, st.session_state.response, "No satisfactoria")
