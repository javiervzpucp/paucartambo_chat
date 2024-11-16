import requests
import json

# Updated API key with correct permissions
api_key = "zwt_nDJrRwRHtr31pOA0qHxov2hKV61hdrbFupsptQ"

# API endpoint
url = "https://api.vectara.io/v2/corpora/paucartambo/documents"

# Payload
payload = {
    "id": "my-doc-id",  # Unique document ID
    "type": "core",  # Document type
    "metadata": {
        "title": "A Nice Document",
        "lang": "eng"
    },
    "document_parts": [
        {
            "text": "I'm a nice document part.",
            "metadata": {
                "nice_rank": 9000
            }
        }
    ]
}

# Headers
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-api-key": api_key
}

# POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Response handling
if response.status_code == 200:
    print("Document successfully uploaded:", response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")


