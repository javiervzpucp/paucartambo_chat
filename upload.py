import requests

# Vectara API Configuration
API_URL = "https://api.vectara.io/v1/query"
API_KEY = "zwt_nDJrR3X2jvq60t7xt0kmBzDOEWxIGt8ZJqloiQ"
CUSTOMER_ID = "2620549959"
CORPUS_ID = 2  # Your Corpus ID
DOCUMENT_ID = "Mascara_Tranformacion_e_Identidad_en_los.pdf"  # Document ID

# Headers for API Authentication
headers = {
    "Accept": "application/json",
    "x-api-key": API_KEY,
}

# Payload to Query for the Document
payload = {
    "query": [
        {
            "query": f"id:{DOCUMENT_ID}",
            "num_results": 1,
            "corpus_key": [
                {"customer_id": CUSTOMER_ID, "corpus_id": CORPUS_ID}
            ]
        }
    ]
}

# Make API Request
response = requests.post(API_URL, json=payload, headers=headers)

# Handle Response
if response.status_code == 200:
    result = response.json()
    if "results" in result and result["results"]:
        document = result["results"][0]
        print("Document retrieved successfully:")
        print(document)
    else:
        print("No document found with the specified ID.")
else:
    print(f"Error fetching document. Status code: {response.status_code}")
    print(f"Response: {response.text}")
