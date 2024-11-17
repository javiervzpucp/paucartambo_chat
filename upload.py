# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 11:08:21 2024
@author: jveraz
"""

from langchain_community.vectorstores import Vectara
from dotenv import load_dotenv
from datetime import datetime
import os
#from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatOpenAI

from neo4j import GraphDatabase
#import openai
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
neo4j_url = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_pass = os.getenv("NEO4J_PASSWORD")

print(openai_api_key)