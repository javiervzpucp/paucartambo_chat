# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
import networkx as nx

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

# Crear el grafo manualmente
@st.cache_resource
def create_manual_knowledge_graph():
    G = nx.DiGraph()

    # Extraer documentos desde Vectara
    vectara_docs = vectara.query(" ")
    texts = [doc["text"] for doc in vectara_docs["documents"]]

    # Construir nodos y relaciones del grafo
    for text in texts:
        # Extraer relaciones del texto (simulado para este ejemplo)
        # En producción, usar una función para extraer relaciones.
        G.add_node(text[:50], content=text)  # Usar una parte del texto como identificador
    return G

# Configurar Streamlit
st.title("Prototipo de Chat con Grafo de Conocimiento Manual")

# Inicializar el grafo de conocimiento
knowledge_graph = create_manual_knowledge_graph()

# Mostrar nodos del grafo
if st.checkbox("Mostrar nodos del grafo"):
    st.write("Nodos del grafo:")
    st.write(list(knowledge_graph.nodes))

# Prompt Template
graph_prompt = PromptTemplate(
    input_variables=["query", "knowledge_str"],
    template="Responde la siguiente pregunta usando este conocimiento: \nPregunta: {query}\nConocimiento: {knowledge_str}",
)

# Entrada del usuario
query = st.text_input("Haz una pregunta relacionada con las Devociones Marianas de Paucartambo:")

if st.button("Responder"):
    if query:
        # Obtener conocimiento del grafo
        knowledge_str = ". ".join([data["content"] for _, data in knowledge_graph.nodes(data=True)])
        
        # Formatear el prompt con el conocimiento y la consulta
        prompt_text = graph_prompt.format(query=query, knowledge_str=knowledge_str)
        
        # Obtener la respuesta del modelo
        response = llm.predict(prompt_text)
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
