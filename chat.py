# -*- coding: utf-8 -*-
"""
Prototipo de chat con grafo de conocimiento
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
from datetime import datetime
from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt
import json

# Cargar variables de entorno desde .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_pass = os.getenv("NEO4J_PASSWORD")

# Configuración de Vectara
vectara = Vectara(
    vectara_customer_id="2620549959",
    vectara_corpus_id=2,
    vectara_api_key="zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ",
)

# Inicializar LLM con OpenAI GPT-4
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    openai_api_key=openai_api_key
)

# Configuración de Neo4j para el grafo
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))

# Borrar grafo previo en Neo4j
def clear_graph(tx):
    tx.run("MATCH (n) DETACH DELETE n")

with driver.session() as session:
    session.write_transaction(clear_graph)

# Crear un grafo de conocimiento desde Vectara
@st.cache_resource
def create_knowledge_graph():
    vectara_docs = vectara.query(" ")
    texts = [doc["text"] for doc in vectara_docs["documents"]]
    nx_graph = nx.Graph()
    
    for text in texts:
        # Procesar texto en fragmentos
        chunk_size = 10000
        text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        for chunk in text_chunks:
            document = Document(page_content=chunk)
            llm_transformer = LLMGraphTransformer(llm=llm)
            graph_documents = llm_transformer.convert_to_graph_documents([document])
            
            # Insertar en Neo4j
            with driver.session() as session:
                for doc in graph_documents:
                    for node in doc.nodes:
                        session.write_transaction(
                            lambda tx: tx.run(
                                "CREATE (n:Entity {id: $id, type: $type})",
                                id=node["id"],
                                type=node["type"],
                            )
                        )
                    for edge in doc.relationships:
                        session.write_transaction(
                            lambda tx: tx.run(
                                "MATCH (a:Entity {id: $source_id}), (b:Entity {id: $target_id}) "
                                "CREATE (a)-[:RELATION {type: $type}]->(b)",
                                source_id=edge["source"]["id"],
                                target_id=edge["target"]["id"],
                                type=edge["type"],
                            )
                        )
            
            # Construir NetworkX grafo
            for doc in graph_documents:
                for node in doc.nodes:
                    nx_graph.add_node(node["id"], content=node["type"])
                for edge in doc.relationships:
                    source = edge["source"]["id"]
                    target = edge["target"]["id"]
                    nx_graph.add_edge(source, target, relationship=edge["type"])
    
    # Guardar grafo como JSON y PNG
    nx_data = nx.node_link_data(nx_graph)
    with open("saved_graph.json", "w") as f:
        json.dump(nx_data, f)
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(nx_graph)
    nx.draw(nx_graph, pos, with_labels=True, node_size=500, node_color="gold", edge_color="black", font_size=8)
    plt.savefig("graph.png")
    return nx_graph

# Inicializar grafo
knowledge_graph = create_knowledge_graph()

# Interfaz de usuario con Streamlit
st.title("Prototipo de Chat con Grafo de Conocimiento")

query = st.text_input("Haz una pregunta relacionada con las Devociones Marianas de Paucartambo:")

if st.button("Responder"):
    if query:
        # Extraer conocimiento del grafo
        subgraph = nx.ego_graph(knowledge_graph, query, radius=1)  # Cambia `radius` para mayor contexto
        knowledge_str = "\n".join([f"{node}: {data['content']}" for node, data in subgraph.nodes(data=True)])
        
        # Generar respuesta usando el conocimiento
        prompt = f"Usa el siguiente conocimiento para responder:\n{knowledge_str}\nPregunta: {query}"
        response = llm.invoke(prompt)
        st.write("**Respuesta:**", response)
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Guardar respuesta en Vectara
def save_to_vectara(query, response, satisfaction, document_id="2560b95df098dda376512766f44af3e0"):
    try:
        vectara.add_texts(
            texts=[
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Query: {query}\n"
                f"Response: {response}\n"
                f"Satisfaction: {satisfaction}"
            ],
            document_id=document_id
        )
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Feedback del usuario
col1, col2 = st.columns(2)
with col1:
    if st.button("👍 Satisfactoria"):
        save_to_vectara(query, response, "Satisfactoria")
with col2:
    if st.button("👎 No satisfactoria"):
        save_to_vectara(query, response, "No satisfactoria")
