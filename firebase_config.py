import os
import firebase_admin
from firebase_admin import credentials, firestore
import json

firebase_json = os.environ.get("FIREBASE_KEY")

if not firebase_json:
    raise Exception("FIREBASE_KEY não encontrada nas variáveis de ambiente do Render")

cred = credentials.Certificate(json.loads(firebase_json))

# evita erro se já inicializou (Render reloads podem duplicar init)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
