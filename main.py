from flask import request, redirect
from monster import render, Flask
import sys, json

app = Flask(__name__)

@app.get("/")
def home():
    signals=open("public/signals.js").read()
    return render("index", locals())

app.run(host="127.0.0.1", port=int(sys.argv[1]))