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

# Inicializar estado de sesión
if "query" not in st.session_state:
    st.session_state.query = ""
if "response" not in st.session_state:
    st.session_state.response = ""
if "user_history" not in st.session_state:
    st.session_state.user_history = []
if "dynamic_questions" not in st.session_state:
    st.session_state.dynamic_questions = []

# Función para generar preguntas dinámicas
def generar_preguntas_dinamicas(historial, n=3):
    recomendaciones = []
    if not historial:
        # Generar preguntas iniciales si no hay historial
        return [
            "¿Qué danzas participan en la festividad?",
            "¿Cuál es el significado de las vestimentas?",
            "¿Cómo se originaron las devociones marianas?",
        ]
    for consulta in historial[-5:]:  # Tomar las últimas 5 consultas para contexto
        response = vectara.as_chat(config).invoke(
            f"Basándote en la pregunta '{consulta}', sugiere consultas relacionadas."
        )
        if response and "answer" in response:
            preguntas = response["answer"].split("\n")
            recomendaciones.extend(preguntas)

    # Filtrar duplicados y devolver hasta N preguntas únicas
    preguntas_unicas = list(set([p.strip() for p in recomendaciones if p.strip()]))
    return preguntas_unicas[:n]

# Mantener 3 preguntas dinámicas
if len(st.session_state.dynamic_questions) < 3:
    nuevas_preguntas = generar_preguntas_dinamicas(
        st.session_state.user_history, 
        n=3 - len(st.session_state.dynamic_questions)
    )
    st.session_state.dynamic_questions.extend(nuevas_preguntas)

# Título
st.title("Prototipo de chat sobre las Devociones Marianas de Paucartambo")

# Imagen
st.image(
    "https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png",
    caption="Virgen del Carmen de Paucartambo",
    use_container_width=True,
)

# Preguntas dinámicas
st.write("**Preguntas sugeridas dinámicas:**")
preguntas_a_mostrar = st.session_state.dynamic_questions[:3]  # Mostrar hasta 3 preguntas dinámicas
for i, pregunta in enumerate(preguntas_a_mostrar):
    if st.button(f"Pregunta {i+1}: {pregunta}"):
        st.session_state.query = pregunta
        st.session_state.user_history.append(pregunta)  # Agregar al historial
        nuevas_preguntas = generar_preguntas_dinamicas([pregunta], n=1)  # Generar una nueva
        st.session_state.dynamic_questions.remove(pregunta)  # Eliminar la seleccionada
        st.session_state.dynamic_questions.extend(nuevas_preguntas)  # Añadir nuevas preguntas
        break  # Salir tras procesar el clic

# Entrada para consultas personalizadas
query_str = st.text_input(
    "Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:",
    value=st.session_state.query,
)

# Botón para responder
if st.button("Responder"):
    if query_str.strip():
        with st.spinner("Generando respuesta..."):
            st.session_state.query = query_str
            rag = vectara.as_chat(config)
            response = rag.invoke(query_str)
            st.session_state.response = response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
            st.session_state.user_history.append(query_str)  # Añadir consulta al historial
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Mostrar respuesta
st.write("**Respuesta:**")
if st.session_state.response:
    st.session_state.response = st.text_area(
        "Edita la respuesta antes de guardar:",
        value=st.session_state.response,
        height=150,
    )

# Guardar respuestas satisfactorias en Vectara
def guardar_respuesta(query, response, satisfaction):
    try:
        vectara.add_texts(
            texts=[
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Query: {query}\n"
                f"Response: {response}\n"
                f"Satisfaction: {satisfaction}"
            ]
        )
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada correctamente!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Botones de retroalimentación
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Sí"):
        guardar_respuesta(st.session_state.query, st.session_state.response, "Satisfactoria")
with col2:
    if st.button("👎 No"):
        guardar_respuesta(st.session_state.query, st.session_state.response, "No satisfactoria")
