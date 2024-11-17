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
import requests
from langchain.document_loaders import TextLoader
from langchain.chains.graph import GraphChain
from langchain.graphs.networkx_graph import NetworkxEntityGraph
import networkx as nx
from datetime import datetime
import pyvis.network as net
from streamlit.components.v1 import html

# Configuración de Vectara
VECTARA_API_URL = "https://api.vectara.io/v2/query"
VECTARA_API_KEY = "zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ"
VECTARA_CORPUS_ID = 2
VECTARA_CUSTOMER_ID = "2620549959"

# Inicializar session state para persistir datos
if "query" not in st.session_state:
    st.session_state.query = ""
if "response" not in st.session_state:
    st.session_state.response = ""
if "graph" not in st.session_state:
    st.session_state.graph = None

# Función para obtener documentos desde Vectara
def fetch_documents_from_vectara():
    """
    Llama a la API de Vectara para obtener documentos relevantes.

    Returns:
        list: Lista de documentos con texto.
    """
    headers = {
        "Authorization": f"Bearer {VECTARA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": {"query": "Devociones Marianas Paucartambo"},
        "customer_id": VECTARA_CUSTOMER_ID,
        "corpus_id": [VECTARA_CORPUS_ID],
        "num_results": 5,
    }

    response = requests.post(VECTARA_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        results = response.json().get("results", [])
        return [{"text": result["snippet"]} for result in results]
    else:
        raise Exception(f"Error fetching documents from Vectara: {response.text}")

# Función para construir un Knowledge Graph
def build_knowledge_graph(documents):
    """
    Construye un Knowledge Graph usando LangChain y NetworkX.

    Args:
        documents (list): Lista de documentos con texto para procesar.

    Returns:
        NetworkxEntityGraph: Grafo con entidades y relaciones extraídas.
    """
    graph = NetworkxEntityGraph(graph=nx.MultiDiGraph())
    processed_docs = [TextLoader(doc["text"]).load() for doc in documents]
    graph_chain = GraphChain.from_documents(processed_docs, graph=graph)
    graph_chain.run()
    return graph

# Visualización del Knowledge Graph
def visualize_knowledge_graph(graph):
    """
    Genera una visualización del grafo usando Pyvis.

    Args:
        graph (NetworkxEntityGraph): Knowledge Graph.

    Returns:
        None
    """
    net_graph = net.Network(height="600px", width="100%", directed=True)
    
    # Añadir nodos y bordes desde NetworkX
    for node in graph.graph.nodes:
        net_graph.add_node(node, label=node)
    for edge in graph.graph.edges(data=True):
        net_graph.add_edge(edge[0], edge[1], title=edge[2].get("relation", ""))

    # Guardar el grafo en HTML y renderizarlo en Streamlit
    path = "/tmp/graph.html"
    net_graph.show(path)
    with open(path, "r", encoding="utf-8") as f:
        html(f.read(), height=600)

# Interfaz de usuario
st.title("Devociones Marianas de Paucartambo")

st.sidebar.title("Opciones")
option = st.sidebar.radio("Seleccione una acción:", ["Consultar", "Ver Knowledge Graph"])

if option == "Consultar":
    # Preguntas sugeridas
    preguntas_sugeridas = [
        "¿Qué danzas se presentan en honor a la Mamacha Carmen?",
        "¿Cuál es el origen de las devociones marianas en Paucartambo?",
        "¿Qué papeles tienen los diferentes grupos de danza en la festividad?",
        "¿Cómo se celebra la festividad de la Virgen del Carmen?",
        "¿Cuál es el significado de las vestimentas en las danzas?",
    ]

    st.write("**Preguntas sugeridas**")
    for pregunta in preguntas_sugeridas:
        if st.button(pregunta):
            st.session_state.query = pregunta

    # Entrada personalizada
    query_str = st.text_input("Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:", value=st.session_state.query)

    if st.button("Responder"):
        if query_str.strip():
            st.session_state.query = query_str
            rag = vectara.as_chat(config)
            response = rag.invoke(query_str)
            st.session_state.response = response.get("answer", "No se encontró información relevante.")
        else:
            st.warning("Por favor, ingresa una pregunta válida.")

    # Mostrar respuesta
    st.write("**Respuesta (editable):**")
    st.session_state.response = st.text_area("Edita la respuesta antes de guardar:", value=st.session_state.response, height=150)

    # Botones de retroalimentación
    st.write("**¿Esta respuesta fue satisfactoria?**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Sí"):
            st.success("Gracias por tu retroalimentación.")
    with col2:
        if st.button("👎 No"):
            st.info("Gracias por ayudarnos a mejorar.")

elif option == "Ver Knowledge Graph":
    st.write("**Knowledge Graph Generado**")
    if not st.session_state.graph:
        with st.spinner("Cargando documentos y construyendo el Knowledge Graph..."):
            documents = fetch_documents_from_vectara()
            st.session_state.graph = build_knowledge_graph(documents)
    visualize_knowledge_graph(st.session_state.graph)
