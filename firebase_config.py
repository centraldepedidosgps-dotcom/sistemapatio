import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Pega a chave do Firebase do ambiente
firebase_json = os.environ.get("FIREBASE_KEY")
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(firebase_json))
    firebase_admin.initialize_app(cred)

db = firestore.client()
