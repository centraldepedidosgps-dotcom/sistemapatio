import os
import firebase_admin
from firebase_admin import credentials, firestore
import json

firebase_json = os.environ.get("FIREBASE_KEY")

cred = credentials.Certificate(json.loads(firebase_json))

firebase_admin.initialize_app(cred)

db = firestore.client()
