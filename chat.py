# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from langchain.chains.graph import GraphChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.graphs import KnowledgeGraph
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

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

# Crear el grafo de conocimiento
@st.cache_resource
def create_knowledge_graph():
    # Extraer documentos desde Vectara
    vectara_docs = vectara.query(" ")
    texts = [doc["text"] for doc in vectara_docs["documents"]]

    # Crear un grafo de conocimiento a partir de los textos
    knowledge_graph = KnowledgeGraph()
    for text in texts:
        knowledge_graph.add_text(text, llm)

    return knowledge_graph

# Crear una función para construir el grafo de conocimiento
@st.cache_resource
def initialize_graph_chain():
    knowledge_graph = create_knowledge_graph()
    graph_prompt = PromptTemplate(
        input_variables=["query", "knowledge_str"],
        template="Contesta la siguiente pregunta usando el conocimiento disponible.\nPregunta: {query}\nConocimiento: {knowledge_str}",
    )
    return GraphChain(
        llm=llm,
        prompt=graph_prompt,
        graph=knowledge_graph
    )

# Configurar Streamlit
st.title("Prototipo de Chat con Grafo de Conocimiento")

# Inicializar la cadena del grafo
graph_chain = initialize_graph_chain()

# Entrada del usuario
query = st.text_input("Haz una pregunta relacionada con las Devociones Marianas de Paucartambo:")

if st.button("Responder"):
    if query:
        response = graph_chain.run(query=query)
        st.write("**Respuesta:**", response)
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Función para guardar respuestas satisfactorias en Vectara
def save_to_vectara(query, response, satisfaction, document_id="2560b95df098dda376512766f44af3e0"):
    try:
        vectara.add_texts(
            texts=[
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Query: {query}\n"
                f"Response: {response}\n"
                f"Satisfaction: {satisfaction}"
            ],
            document_id=document_id,  # Guardar en el mismo documento
        )
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Retroalimentación del usuario
st.write("**¿Esta respuesta fue satisfactoria?**")
col1, col2 = st.columns(2)

with col1:
    if st.button("👍 Sí"):
        save_to_vectara(query, response, "Satisfactoria")

with col2:
    if st.button("👎 No"):
        save_to_vectara(query, response, "No satisfactoria")
