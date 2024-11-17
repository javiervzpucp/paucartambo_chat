# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from dotenv import load_dotenv
from datetime import datetime
import os
from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
neo4j_url = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_pass = os.getenv("NEO4J_PASSWORD")

# Inicializar cliente de OpenAI
client = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=0,
    openai_api_key=openai_api_key
)

# Configuración de Vectara
vectara = Vectara(
    vectara_customer_id="2620549959",
    vectara_corpus_id=2,
    vectara_api_key="zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ",
)

# Configuración de Neo4j
graph_driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_pass))

# Función para extraer contexto del Knowledge Graph
def extract_context(query):
    """
    Extrae nodos y relaciones relevantes del grafo basados en la consulta del usuario.
    """
    context = []
    with graph_driver.session() as session:
        results = session.run(
            """
            MATCH (n)-[r]->(m)
            WHERE n.name CONTAINS $query OR m.name CONTAINS $query
            RETURN n, r, m
            """,
            query=query
        )
        for record in results:
            context.append(f"{record['n']['name']} -[{record['r']['type']}]-> {record['m']['name']}")
    return "\n".join(context)

# Crear grafo de conocimiento (correr una vez)
@st.cache_resource
def create_knowledge_graph():
    vectara_docs = vectara.query(" ")
    texts = [doc["text"] for doc in vectara_docs["documents"]]
    with graph_driver.session() as session:
        for text in texts:
            session.run(
                """
                CREATE (n:Document {content: $text})
                """,
                text=text
            )
    return "Grafo de conocimiento creado."

# Inicializar Knowledge Graph
knowledge_graph_status = create_knowledge_graph()

# Función para generar respuestas utilizando contexto del Knowledge Graph
def generate_response_from_knowledge_graph(query, context):
    """
    Genera una respuesta basada en el contexto extraído del Knowledge Graph.
    """
    prompt = f"""
    Eres un experto en cultura peruana y tienes conocimiento detallado sobre las Devociones Marianas de Paucartambo.
    Usa el siguiente contexto para responder a la pregunta del usuario:
    
    Contexto:
    {context}
    
    Pregunta:
    {query}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en cultura peruana."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error al interactuar con GPT-4: {e}")
        return "Lo siento, hubo un error al generar la respuesta."

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
            document_id=document_id
        )
        st.success(f"¡Respuesta marcada como '{satisfaction}' y guardada en Vectara!")
    except Exception as e:
        st.error(f"Error al guardar la respuesta en Vectara: {e}")

# Interfaz de Streamlit
st.title("Prototipo de Chat con Grafo de Conocimiento")

query = st.text_input("Haz una pregunta relacionada con las Devociones Marianas de Paucartambo:")

if st.button("Responder"):
    if query.strip():
        context = extract_context(query)
        if context:
            response = generate_response_from_knowledge_graph(query, context)
            st.write("**Respuesta generada:**")
            st.write(response)
        else:
            st.warning("No se encontró contexto relevante en el grafo.")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Retroalimentación del usuario
st.write("**¿Esta respuesta fue satisfactoria?**")
col1, col2 = st.columns(2)

with col1:
    if st.button("👍 Sí"):
        save_to_vectara(query, response, "Satisfactoria")

with col2:
    if st.button("👎 No"):
        save_to_vectara(query, response, "No satisfactoria")
