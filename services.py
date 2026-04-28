from firebase_config import db
import time

# ================= MOTORISTAS =================
def listar_motoristas():
    docs = db.collection("motoristas").stream()

    lista = []
    for d in docs:
        x = d.to_dict()
        x["id"] = d.id
        lista.append(x)

    return lista


def salvar_motorista(nome, uid):
    if not nome or not uid:
        return

    db.collection("motoristas").add({
        "nome": nome,
        "uid": uid,
        "status": "CHEGOU",
        "disponivel": True,
        "em_servico": False,
        "vaga": None,
        "ordem": int(time.time())
    })


def definir_disponibilidade(id, valor):
    db.collection("motoristas").document(id).update({
        "disponivel": valor
    })


def mover_patio(id):
    db.collection("motoristas").document(id).update({
        "status": "PATIO"
    })


def chamar_vaga(id, vaga):
    db.collection("motoristas").document(id).update({
        "status": "VAGA",
        "vaga": vaga,
        "em_servico": True
    })


# ================= FILA INTELIGENTE =================
def chamar_proximo():
    docs = db.collection("motoristas") \
        .where("disponivel", "==", True) \
        .where("em_servico", "==", False) \
        .stream()

    lista = sorted(docs, key=lambda d: d.to_dict().get("ordem", 0))

    for d in lista:
        db.collection("motoristas").document(d.id).update({
            "status": "PATIO"
        })
        return d.id
