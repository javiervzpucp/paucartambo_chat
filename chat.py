import pandas as pd
import streamlit as st
from datetime import datetime

# Path to shared CSV file
SHARED_CSV_FILE = "shared_responses.csv"

# Initialize CSV file if it doesn't exist
def initialize_csv(file_path):
    """
    Create a new CSV file with the appropriate headers if it doesn't exist.
    """
    try:
        # Check if the file already exists
        open(file_path, "r").close()
    except FileNotFoundError:
        # Create a new file with headers
        df = pd.DataFrame(columns=["timestamp", "query", "response"])
        df.to_csv(file_path, index=False)
        st.info("Initialized shared CSV file.")

# Save response to CSV
def save_to_csv(file_path, query, response):
    """
    Save the user's query and response to the shared CSV file.

    Args:
        file_path (str): Path to the shared CSV file.
        query (str): The user's query.
        response (str): The response text.
    """
    try:
        # Load existing data
        data = pd.read_csv(file_path)
        
        # Add a new row
        new_row = {"timestamp": datetime.now().isoformat(), "query": query, "response": response}
        data = data.append(new_row, ignore_index=True)
        
        # Save back to the file
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

# Main Streamlit app
st.title("Shared Responses Collection")

# Initialize the shared CSV file
initialize_csv(SHARED_CSV_FILE)

# Example response data
query = st.text_input("Enter your query", value="What are the dances for the Virgen del Carmen?")
response = "There are several dances, including the Saqras and the Chunchos."

# Buttons for user interaction
if st.button("😊 Save Satisfactory Response"):
    save_to_csv(SHARED_CSV_FILE, query, response)

if st.button("📄 View All Responses"):
    display_csv(SHARED_CSV_FILE)
