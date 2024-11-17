from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI

# Cargar variables de entorno desde .env
load_dotenv()

# Clave de OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
assert openai_api_key, "La clave de OpenAI no está configurada correctamente en .env"

# Imprimir la clave (solo para depuración; no lo hagas en producción)
print(f"Clave de OpenAI cargada: {openai_api_key[:6]}***")

# Inicializar ChatOpenAI
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    openai_api_key=openai_api_key  # Pasar la clave explícitamente
)

# Probar el modelo con un mensaje de ejemplo
try:
    response = llm.predict("¿Cuál es la capital de Francia?")
    print(f"Respuesta del modelo: {response}")
except Exception as e:
    print(f"Error al inicializar el modelo: {e}")
