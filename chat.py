# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024

@author: jveraz
"""

import os
from dotenv import load_dotenv
import streamlit as st
from langchain_community.vectorstores import Vectara
from langchain_community.vectorstores.vectara import (
    RerankConfig,
    SummaryConfig,
    VectaraQueryConfig,
)
from langchain.llms import OpenAI
import networkx as nx
from pyvis.network import Network
from datetime import datetime

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    openai_api_key=openai_api_key
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

# Inicializar el estado de la aplicación
if "query" not in st.session_state:
    st.session_state.query = ""
if "response" not in st.session_state:
    st.session_state.response = ""
if "graph" not in st.session_state:
    st.session_state.graph = None

# Título
st.title("Prototipo de chat y grafo de conocimiento sobre Devociones Marianas")

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

st.write("**Preguntas sugeridas:**")
for pregunta in preguntas_sugeridas:
    if st.button(pregunta):
        st.session_state.query = pregunta

# Entrada personalizada
query_str = st.text_input("Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:", value=st.session_state.query)

# Construcción del Knowledge Graph
def build_knowledge_graph():
    graph = nx.MultiDiGraph()

    try:
        # Recuperar documentos desde Vectara
        documents = vectara.query("Devociones Marianas", config)
        for doc in documents:
            text = doc["text"]
            sentences = text.split(".")  # Dividir el texto en oraciones simples
            for sentence in sentences:
                parts = sentence.split(" -> ")  # Formato esperado: entidad1 -> relación -> entidad2
                if len(parts) == 3:
                    entity1, relation, entity2 = parts
                    graph.add_edge(entity1.strip(), entity2.strip(), relation=relation.strip())
    except Exception as e:
        st.error(f"Error al construir el grafo de conocimiento: {e}")
    return graph

# Visualizar el grafo con Pyvis
def visualize_graph(graph):
    net_graph = Network(height="600px", width="100%", directed=True)
    for node in graph.nodes:
        net_graph.add_node(node, label=node)
    for edge in graph.edges(data=True):
        net_graph.add_edge(edge[0], edge[1], title=edge[2]["relation"])
    net_graph.show("graph.html")
    st.markdown("[Ver el grafo de conocimiento](graph.html)")

# Responder utilizando el grafo
def answer_from_graph(graph, query):
    for edge in graph.edges(data=True):
        if query.lower() in edge[0].lower() or query.lower() in edge[2]["relation"].lower():
            return f"De acuerdo al grafo: {edge[0]} -> {edge[2]['relation']} -> {edge[1]}"
    return None

# Guardar respuestas en Vectara
def save_to_vectara(query, response, satisfaction, document_id="2560b95df098dda376512766f44af3e0"):
    """
    Guardar la respuesta marcada como satisfactoria o no en un documento específico de Vectara.
    """
    try:
        vectara.add_texts(
            texts=[
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Query: {query}\n"
                f"Response: {response}\n"
                f"Satisfaction: {satisfaction}"
            ],
            document_id=document_id,
        )
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Procesar la consulta
if st.button("Responder"):
    if query_str.strip():
        st.session_state.query = query_str

        # Intentar responder desde el grafo
        if st.session_state.graph is None:
            st.session_state.graph = build_knowledge_graph()
        graph_response = answer_from_graph(st.session_state.graph, query_str)

        if graph_response:
            st.session_state.response = graph_response
        else:
            # Si no hay respuesta en el grafo, usar el modelo
            rag = vectara.as_chat(config)
            response = rag.invoke(query_str)
            st.session_state.response = response.get("answer", "Lo siento, no tengo suficiente información para responder a tu pregunta.")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Mostrar respuesta
st.write("**Respuesta (editable):**")
if st.session_state.response:
    st.session_state.response = st.text_area(
        "Edita la respuesta antes de guardar:",
        value=st.session_state.response,
        height=150,
    )

# Botones de retroalimentación
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Satisfactoria"):
        save_to_vectara(st.session_state.query, st.session_state.response, "Satisfactoria")
with col2:
    if st.button("👎 No satisfactoria"):
        save_to_vectara(st.session_state.query, st.session_state.response, "No satisfactoria")

# Generar el grafo de conocimiento
if st.button("Generar Grafo de Conocimiento"):
    if st.session_state.graph is None:
        st.session_state.graph = build_knowledge_graph()
    if st.session_state.graph:
        visualize_graph(st.session_state.graph)
