import pyrebase4 as pyrebase

config = {
    "apiKey": "AIzaSyB9HGNeqejP-_b-229r3U6giwMnxUZ2smU",
    "authDomain": "sistemapatio-5fbe5.firebaseapp.com",
    "projectId": "sistemapatio-5fbe5",
    "storageBucket": "sistemapatio-5fbe5.appspot.com",
    "messagingSenderId": "953703344743",
    "appId": "1:953703344743:web:0b2ad418f9004a325702c2",

    # 🔥 ISSO AQUI É O QUE FALTA
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
