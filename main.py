from flask import request, redirect
from monster import render, Flask
import sys, json, os, threading

app = Flask(__name__)

def start_ollama():
    os.system("ollam serve")

threading.Thread(target=start_ollama).start()

@app.get("/")
def home():
    response=Flask.response_class(render("index", locals()).render)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

app.run(host="127.0.0.1", port=int(sys.argv[1]))