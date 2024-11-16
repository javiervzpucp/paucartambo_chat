import pandas as pd
import streamlit as st
from datetime import datetime
from langchain_community.vectorstores import Vectara
from langchain_community.vectorstores.vectara import (
    RerankConfig,
    SummaryConfig,
    VectaraQueryConfig,
)

# Path to shared CSV file
SHARED_CSV_FILE = "shared_responses.csv"

# Initialize CSV file if it doesn't exist
def initialize_csv(file_path):
    """
    Create a new CSV file with the appropriate headers if it doesn't exist.
    """
    try:
        open(file_path, "r").close()
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp", "query", "response"])
        df.to_csv(file_path, index=False)
        st.info("Initialized shared CSV file.")

# Save response to CSV
def save_to_csv(file_path, query, response):
    """
    Save the user's query and response to the shared CSV file.
    """
    try:
        data = pd.read_csv(file_path)
        new_row = {"timestamp": datetime.now().isoformat(), "query": query, "response": response}
        data = data.append(new_row, ignore_index=True)
        data.to_csv(file_path, index=False)
        st.success("Response saved successfully!")
    except Exception as e:
        st.error(f"Error saving response to CSV: {e}")

# Display the contents of the shared CSV file
def display_csv(file_path):
    """
    Display the contents of the shared CSV file in the Streamlit app.
    """
    try:
        data = pd.read_csv(file_path)
        st.write(data)
    except FileNotFoundError:
        st.error("Shared CSV file not found. It will be initialized when the first response is saved.")

# Vectara configuration
vectara = Vectara(
    vectara_customer_id="2620549959",
    vectara_corpus_id=2,
    vectara_api_key="zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ"
)

summary_config = SummaryConfig(is_enabled=True, max_results=5, response_lang="spa")
rerank_config = RerankConfig(reranker="mmr", rerank_k=50, mmr_diversity_bias=0.1)

config = VectaraQueryConfig(
    k=10, lambda_val=0.0, rerank_config=rerank_config, summary_config=summary_config
)

# Main Streamlit app
st.markdown("<h1 style='font-size: 36px;'>Prototipo de chat sobre Devociones Marianas de Paucartambo</h1>", unsafe_allow_html=True)

# Display image
st.image("https://raw.githubusercontent.com/javiervzpucp/paucartambo/main/imagenes/1.png", caption="Virgen del Carmen de Paucartambo", use_container_width=True)

# Suggested questions
preguntas_sugeridas = [
    "¿Qué danzas se presentan en honor a la Mamacha Carmen?",
    "¿Cuál es el origen de las devociones marianas en Paucartambo?",
    "¿Qué papeles tienen los diferentes grupos de danza en la festividad?",
    "¿Cómo se celebra la festividad de la Virgen del Carmen?",
    "¿Cuál es el significado de las vestimentas en las danzas?",
]

# Initialize the shared CSV file
initialize_csv(SHARED_CSV_FILE)

# Dropdown for suggested questions
selected_question = st.selectbox("Preguntas sugeridas:", preguntas_sugeridas, index=0)

# Text input for custom query
query_str = st.text_input("Pregunta algo sobre Devociones Marianas o Danzas de Paucartambo:", value=selected_question)

# Call Vectara to get the response
rag = vectara.as_chat(config)
resp = rag.invoke(query_str)

# Display response
st.write("**Respuesta:**")
st.write(resp.get('answer', "No se encontró una respuesta adecuada."))

# Buttons for saving and viewing responses
col1, col2 = st.columns(2)

with col1:
    if st.button("😊 Guardar respuesta satisfactoria"):
        save_to_csv(SHARED_CSV_FILE, query_str, resp.get('answer', ""))
        st.success("¡Tu respuesta se guardó exitosamente!")

with col2:
    if st.button("📄 Ver todas las respuestas"):
        display_csv(SHARED_CSV_FILE)

# Download button for the CSV file
if st.button("📥 Descargar CSV"):
    try:
        with open(SHARED_CSV_FILE, "r") as file:
            st.download_button(
                label="Descargar archivo CSV",
                data=file,
                file_name="shared_responses.csv",
                mime="text/csv",
            )
    except FileNotFoundError:
        st.error("No se encontró el archivo CSV para descargar.")
