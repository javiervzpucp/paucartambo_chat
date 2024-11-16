# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 14:18:19 2024

@author: jveraz
"""

import requests

url = "https://api.vectara.io/v1/index"
headers = {
    "Authorization": f"Bearer zqt_nDJrRzuEwpSstPngTiTio43sQzykyJ1x6PebAQ",  # Replace with your new API key
    "Content-Type": "application/json",
}

data = {
    "customer_id": "2620549959",  # Replace with your customer ID
    "corpus_id": "2",                  # Replace with your corpus ID
    "document": {
        "document_id": "test-doc",
        "title": "Test Upload",
        "section": [
            {
                "text": "Testing Vectara integration.",
                "lang": "en",
            }
        ],
    },
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print("Upload successful:", response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")
