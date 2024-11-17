# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

import streamlit as st
from langchain_community.vectorstores import Vectara
from langchain.chat_models import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from neo4j import GraphDatabase
from dotenv import load_dotenv
from datetime import datetime
import os
from PyPDF2 import PdfReader

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de credenciales
openai_api_key = st.secrets['openai']["OPENAI_API_KEY"]
vectara_customer_id = 2620549959
vectara_corpus_id = 2
vectara_api_key = "zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ"
neo4j_url = "neo4j+s://8c9ab5cb.databases.neo4j.io"
neo4j_user = "neo4j"
neo4j_pass = "EsxnRgeaaaGcqKSslig3di1IAl5l51yIj39lj7wWhyQ"

# Validar que todas las variables se hayan cargado correctamente
if not openai_api_key:
    raise ValueError("Falta la API Key de OpenAI. Configúrala en el archivo .env")
if not vectara_customer_id or not vectara_corpus_id or not vectara_api_key:
    raise ValueError("Falta información de Vectara. Configúrala en el archivo .env")

# Inicializar cliente de OpenAI
client = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=0,
    openai_api_key=openai_api_key
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
            WHERE n.content CONTAINS $query OR m.content CONTAINS $query
            RETURN n, r, m
            """,
            query=query
        )
        for record in results:
            context.append(f"{record['n']['content']} -[{record['r']['type']}]-> {record['m']['content']}")
    return "\n".join(context)

# Función para procesar archivos PDF y TXT desde la carpeta "documentos"
def create_knowledge_graph():
    """
    Crea un grafo de conocimiento procesando documentos PDF y TXT en la carpeta 'documentos'.
    """
    folder_path = "documentos"  # Carpeta donde están los PDFs y TXT
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"La carpeta '{folder_path}' no existe.")

    texts = []
    # Leer y procesar los PDFs y TXT
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if filename.endswith(".pdf"):
                pdf_reader = PdfReader(file_path)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()
                texts.append(pdf_text)
            elif filename.endswith(".txt"):
                with open(file_path, "r", encoding='latin-1') as txt_file:
                    texts.append(txt_file.read())
        except Exception as e:
            st.error(f"Error al leer el archivo {filename}: {e}")

    # Generar grafo a partir de los textos extraídos
    llm_transformer = LLMGraphTransformer(llm=client)

    with graph_driver.session() as session:
        for text in texts:
            document = Document(page_content=text)
            graph_documents = llm_transformer.convert_to_graph_documents([document])

            for graph_doc in graph_documents:
                for node in graph_doc.nodes:
                    session.run(
                        """
                        MERGE (n:Node {id: $id, content: $content})
                        """,
                        id=node.get("id"),
                        content=node.get("type")
                    )
                for edge in graph_doc.relationships:
                    session.run(
                        """
                        MATCH (a:Node {id: $source}), (b:Node {id: $target})
                        MERGE (a)-[r:RELATION {type: $type}]->(b)
                        """,
                        source=edge["source"]["id"],
                        target=edge["target"]["id"],
                        type=edge["type"]
                    )
    return "Grafo de conocimiento creado desde archivos PDF y TXT."

# Inicializar Knowledge Graph
try:
    knowledge_graph_status = create_knowledge_graph()
    st.success(knowledge_graph_status)
except Exception as e:
    st.error(f"Error al crear el grafo de conocimiento: {e}")

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

# Función para mostrar preguntas recomendadas
def display_recommended_questions(questions):
    """
    Muestra preguntas recomendadas como botones en Streamlit.
    """
    st.write("**Preguntas recomendadas:**")
    for question in questions:
        if st.button(question):
            return question
    return None

# Interfaz de Streamlit
st.title("Prototipo de Chat con Grafo de Conocimiento")

# Preguntas recomendadas
recommended_questions = [
    "¿Cuál es el origen de las Devociones Marianas?",
    "¿Qué significa la Virgen del Carmen en Paucartambo?",
    "¿Cómo se celebra la fiesta de la Virgen del Rosario?",
]

selected_question = display_recommended_questions(recommended_questions)

# Entrada del usuario o pregunta seleccionada
query = st.text_input("Haz una pregunta relacionada con las Devociones Marianas de Paucartambo:", value=selected_question or "")

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
