import os
import time
import flet as ft
from firebase_auth import auth
from firebase_config import db

# ================= UTIL =================
def hoje():
    return time.strftime("%Y-%m-%d")

# ================= FIREBASE =================
def abrir_disponibilidade(data):
    doc = db.collection("disponibilidade").document(data).get()
    if doc.exists:
        return False
    db.collection("disponibilidade").document(data).set({
        "data": data,
        "status": "ABERTA"
    })
    return True

def excluir_disponibilidade(data):
    db.collection("disponibilidade").document(data).delete()

def marcar_presenca(data, motorista):
    docs = db.collection("presenca") \
        .where("data", "==", data) \
        .where("motorista_id", "==", motorista["id"]) \
        .stream()
    if list(docs):
        return False
    db.collection("presenca").add({
        "data": data,
        "motorista_id": motorista["id"],
        "nome": motorista["nome"],
        "status": "AGUARDANDO"
    })
    return True

def adicionar_escala(p):
    db.collection("escalas").add({
        "data": p["data"],
        "motorista_id": p["motorista_id"],
        "nome": p["nome"],
        "turno": p["turno"],
        "codigo": p["codigo"]
    })

def resetar():
    for c in ["disponibilidade", "presenca", "escalas"]:
        for d in db.collection(c).stream():
            db.collection(c).document(d.id).delete()

def promover_admin(uid):
    db.collection("usuarios").document(uid).set({"tipo": "admin"}, merge=True)

def garantir_usuario(uid, email):
    ref = db.collection("usuarios").document(uid)
    doc = ref.get()
    if not doc.exists:
        ref.set({"tipo": "motorista", "email": email})

# ================= APP =================
def main(page: ft.Page):
    page.title = "Sistema de Escala"
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO

    listeners = []

    def add_listener(l):
        listeners.append(l)

    def clear_listeners():
        for l in listeners:
            try:
                l()
            except:
                pass
        listeners.clear()

    def msg(t):
        page.snack_bar = ft.SnackBar(ft.Text(t), open=True)
        page.update()

    def logout(e=None):
        clear_listeners()
        login()

    # ================= LOGIN =================
    def login():
        page.controls.clear()
        email = ft.TextField(label="Email", expand=True)
        senha = ft.TextField(label="Senha", password=True, expand=True)

        def entrar(e):
            try:
                user = auth.sign_in_with_email_and_password(email.value, senha.value)
                uid = user["localId"]
                garantir_usuario(uid, email.value)
                doc = db.collection("usuarios").document(uid).get()
                tipo = doc.to_dict().get("tipo", "motorista")
                if tipo == "admin":
                    admin(uid, email.value)
                else:
                    motorista(uid, email.value)
            except Exception as e:
                msg(str(e))

        page.add(
            ft.Column([
                ft.Text("🚚 Sistema de Escala", size=26, weight="bold"),
                email,
                senha,
                ft.ElevatedButton("Entrar", on_click=entrar)
            ], spacing=10)
        )

    # ================= ADMIN =================
    def admin(uid, nome):
        clear_listeners()
        page.controls.clear()

        data_input = ft.TextField(label="Data", value=hoje(), expand=True)
        col_disp = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        col_presenca = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        col_escala = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        col_users = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def box(title, content, color):
            return ft.Container(
                expand=True,
                padding=10,
                bgcolor=color,
                border_radius=10,
                content=ft.Column([ft.Text(title, weight="bold"), content])
            )

        # LISTENERS
        def listen_disp():
            def snap(col_snapshot, *_):
                col_disp.controls.clear()
                for d in col_snapshot:
                    x = d.to_dict()
                    col_disp.controls.append(
                        ft.Container(
                            padding=8,
                            margin=3,
                            bgcolor="#dbeafe",
                            border_radius=8,
                            content=ft.Row([
                                ft.Text("📅 " + x["data"]),
                                ft.Container(expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color="red",
                                    on_click=lambda e, v=x["data"]: excluir_disponibilidade(v)
                                )
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("disponibilidade").on_snapshot(snap))

        def listen_presenca():
            def snap(col_snapshot, *_):
                col_presenca.controls.clear()
                col_escala.controls.clear()
                for d in col_snapshot:
                    p = d.to_dict()
                    turno = ft.Dropdown(options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], width=100)
                    codigo = ft.TextField(label="Código", width=120)
                    def enviar(e, p=p, turno=turno, codigo=codigo):
                        if not turno.value or not codigo.value:
                            msg("Preencha tudo")
                            return
                        adicionar_escala({
                            "data": p["data"],
                            "motorista_id": p["motorista_id"],
                            "nome": p["nome"],
                            "turno": turno.value,
                            "codigo": codigo.value
                        })
                        msg("Adicionado na escala")
                    col_presenca.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#fef3c7",
                            border_radius=10,
                            content=ft.Column([
                                ft.Text(f"🚛 {p['nome']}"),
                                ft.Text(f"📅 {p['data']}"),
                                turno,
                                codigo,
                                ft.ElevatedButton("Enviar", on_click=enviar)
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("presenca").on_snapshot(snap))

        def listen_escala():
            def snap(col_snapshot, *_):
                col_escala.controls.clear()
                for d in col_snapshot:
                    e = d.to_dict()
                    col_escala.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#dcfce7",
                            border_radius=10,
                            content=ft.Column([
                                ft.Text(f"📅 {e['data']}"),
                                ft.Text(f"🚛 {e['nome']}"),
                                ft.Text(f"Turno: {e['turno']}"),
                                ft.Text(f"Código: {e['codigo']}")
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("escalas").on_snapshot(snap))

        def listen_users():
            def snap(col_snapshot, *_):
                col_users.controls.clear()
                for u in col_snapshot:
                    user = u.to_dict()
                    col_users.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#f3f4f6",
                            border_radius=10,
                            content=ft.Row([
                                ft.Text(u.id),
                                ft.Container(expand=True),
                                ft.Text(user.get("tipo", "")),
                                ft.ElevatedButton("Admin", on_click=lambda e, uid=u.id: promover_admin(uid))
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("usuarios").on_snapshot(snap))

        def criar(e):
            if abrir_disponibilidade(data_input.value):
                msg("Criado")
            else:
                msg("Já existe")

        def reset(e):
            resetar()
            msg("Resetado")

        listen_disp()
        listen_presenca()
        listen_escala()
        listen_users()

        # ================= LAYOUT =================
        page.add(ft.Column([
            ft.Row([
                ft.Text(f"👨‍💼 ADMIN: {nome}", size=20),
                ft.Container(expand=True),
                ft.ElevatedButton("Logout", on_click=logout)
            ]),
            ft.Divider(),
            ft.Column([
                data_input,
                ft.Row([
                    ft.ElevatedButton("Criar", on_click=criar),
                    ft.ElevatedButton("Reset", on_click=reset)
                ])
            ]),
            ft.Divider(),
            ft.Container(
                content=ft.Row([
                    box("📍 Disponibilidade", col_disp, "#dbeafe"),
                    box("🚛 Presença", col_presenca, "#fef3c7"),
                    box("📋 Escala", col_escala, "#dcfce7")
                ], scroll=ft.ScrollMode.AUTO),
                height=500
            ),
            ft.Divider(),
            ft.Text("👥 Usuários"),
            col_users
        ]))

    # ================= MOTORISTA =================
    def motorista(uid, nome):
        clear_listeners()
        page.controls.clear()
        col_disp = ft.Column(scroll=ft.ScrollMode.AUTO)
        col_escala = ft.Column(scroll=ft.ScrollMode.AUTO)

        def listen_disp():
            def snap(col_snapshot, *_):
                col_disp.controls.clear()
                for d in col_snapshot:
                    x = d.to_dict()
                    col_disp.controls.append(
                        ft.Container(
                            padding=8,
                            margin=3,
                            bgcolor="#dbeafe",
                            border_radius=8,
                            content=ft.Row([
                                ft.Text("📅 " + x["data"]),
                                ft.Container(expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color="red",
                                    on_click=lambda e, v=x["data"]: excluir_disponibilidade(v)
                                )
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("disponibilidade").on_snapshot(snap))

        def listen_presenca():
            def snap(col_snapshot, *_):
                col_presenca.controls.clear()
                col_escala.controls.clear()
                for d in col_snapshot:
                    p = d.to_dict()
                    turno = ft.Dropdown(options=[ft.dropdown.Option("AM"), ft.dropdown.Option("PM")], width=100)
                    codigo = ft.TextField(label="Código", width=120)
                    def enviar(e, p=p, turno=turno, codigo=codigo):
                        if not turno.value or not codigo.value:
                            msg("Preencha tudo")
                            return
                        adicionar_escala({
                            "data": p["data"],
                            "motorista_id": p["motorista_id"],
                            "nome": p["nome"],
                            "turno": turno.value,
                            "codigo": codigo.value
                        })
                        msg("Adicionado na escala")
                    col_presenca.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#fef3c7",
                            border_radius=10,
                            content=ft.Column([
                                ft.Text(f"🚛 {p['nome']}"),
                                ft.Text(f"📅 {p['data']}"),
                                turno,
                                codigo,
                                ft.ElevatedButton("Enviar", on_click=enviar)
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("presenca").on_snapshot(snap))

        def listen_escala():
            def snap(col_snapshot, *_):
                col_escala.controls.clear()
                for d in col_snapshot:
                    e = d.to_dict()
                    col_escala.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#dcfce7",
                            border_radius=10,
                            content=ft.Column([
                                ft.Text(f"📅 {e['data']}"),
                                ft.Text(f"🚛 {e['nome']}"),
                                ft.Text(f"Turno: {e['turno']}"),
                                ft.Text(f"Código: {e['codigo']}")
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("escalas").on_snapshot(snap))

        def listen_users():
            def snap(col_snapshot, *_):
                col_users.controls.clear()
                for u in col_snapshot:
                    user = u.to_dict()
                    col_users.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#f3f4f6",
                            border_radius=10,
                            content=ft.Row([
                                ft.Text(u.id),
                                ft.Container(expand=True),
                                ft.Text(user.get("tipo", "")),
                                ft.ElevatedButton("Admin", on_click=lambda e, uid=u.id: promover_admin(uid))
                            ])
                        )
                    )
                page.update()
            add_listener(db.collection("usuarios").on_snapshot(snap))

        def criar(e):
            if abrir_disponibilidade(data_input.value):
                msg("Criado")
            else:
                msg("Já existe")

        def reset(e):
            resetar()
            msg("Resetado")

        listen_disp()
        listen_presenca()
        listen_escala()
        listen_users()

        # ================= LAYOUT =================
        page.add(ft.Column([
            ft.Row([
                ft.Text(f"👨‍💼 ADMIN: {nome}", size=20),
                ft.Container(expand=True),
                ft.ElevatedButton("Logout", on_click=logout)
            ]),
            ft.Divider(),
            ft.Column([
                data_input,
                ft.Row([
                    ft.ElevatedButton("Criar", on_click=criar),
                    ft.ElevatedButton("Reset", on_click=reset)
                ])
            ]),
            ft.Divider(),
            ft.Container(
                content=ft.Row([
                    box("📍 Disponibilidade", col_disp, "#dbeafe"),
                    box("🚛 Presença", col_presenca, "#fef3c7"),
                    box("📋 Escala", col_escala, "#dcfce7")
                ], scroll=ft.ScrollMode.AUTO),
                height=500
            ),
            ft.Divider(),
            ft.Text("👥 Usuários"),
            col_users
        ]))

    # ================= MOTORISTA =================
    def motorista(uid, nome):
        clear_listeners()
        page.controls.clear()
        col_disp = ft.Column(scroll=ft.ScrollMode.AUTO)
        col_escala = ft.Column(scroll=ft.ScrollMode.AUTO)

        def listen_disp():
            def snap(col_snapshot, *_):
                col_disp.controls.clear()

                for d in col_snapshot:
                    x = d.to_dict()

                    def marcar(data):
                        def i(e):
                            if marcar_presenca(data, {"id": uid, "nome": nome}):
                                msg("OK")
                            else:
                                msg("Já marcou")
                        return i

                    col_disp.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#eff6ff",
                            border_radius=10,
                            content=ft.Row([
                                ft.Text(x["data"]),
                                ft.Container(expand=True),
                                ft.ElevatedButton("✔", on_click=marcar(x["data"]))
                            ])
                        )
                    )

                page.update()

            add_listener(db.collection("disponibilidade").on_snapshot(snap))

        def listen_escala():
            def snap(col_snapshot, *_):
                col_escala.controls.clear()

                for d in col_snapshot:
                    e = d.to_dict()

                    col_escala.controls.append(
                        ft.Container(
                            padding=10,
                            margin=5,
                            bgcolor="#f0fdf4",
                            border_radius=10,
                            content=ft.Column([
                                ft.Text(e["data"]),
                                ft.Text(e["nome"]),
                                ft.Text(e["turno"]),
                                ft.Text(e["codigo"])
                            ])
                        )
                    )

                page.update()

            add_listener(db.collection("escalas").where("motorista_id", "==", uid).on_snapshot(snap))

        listen_disp()
        listen_escala()

        page.add(
            ft.Column([
                ft.Row([
                    ft.Text(f"🚛 {nome}", size=20),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Logout", on_click=logout)
                ]),
                col_disp,
                col_escala
            ])
        )

    login()


ft.app(target=main)
