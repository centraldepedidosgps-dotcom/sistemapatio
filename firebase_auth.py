# firebase_auth.py
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Inicializa Firebase Admin
firebase_json = os.environ.get("FIREBASE_KEY")
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(firebase_json))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================= FUNÇÕES DE AUTENTICAÇÃO =================

def criar_usuario(email: str, senha: str, tipo: str = "motorista") -> str:
    """
    Cria um usuário no Firebase Auth e registra no Firestore.
    Retorna o UID do usuário criado.
    """
    user = auth.create_user(email=email, password=senha)
    uid = user.uid
    db.collection("usuarios").document(uid).set({"tipo": tipo, "email": email})
    return uid

def obter_usuario(uid: str) -> dict:
    """
    Retorna os dados do usuário pelo UID.
    """
    doc = db.collection("usuarios").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

def promover_admin(uid: str):
    """
    Promove um usuário existente a admin.
    """
    db.collection("usuarios").document(uid).set({"tipo": "admin"}, merge=True)

def garantir_usuario(uid: str, email: str):
    """
    Cria registro do usuário no Firestore se não existir.
    """
    ref = db.collection("usuarios").document(uid)
    if not ref.get().exists:
        ref.set({"tipo": "motorista", "email": email})

def verificar_token(id_token: str) -> dict:
    """
    Verifica um token JWT do Firebase Auth e retorna o UID e email.
    """
    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token["uid"]
    email = decoded_token.get("email")
    return {"uid": uid, "email": email}
