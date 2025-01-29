from flask import request, redirect
from monster import render, Flask
import sys, json, os, threading, llm, flask

app = Flask(__name__)
marked="<script>"+open("public/marked.js").read()+"</script>"

def start_ollama():
    os.system("ollam run deepseek-coder-v2")

messages=[]

threading.Thread(target=start_ollama).start()

@app.get("/")
def home():
    response=Flask.response_class(render("index", globals() | locals()).render)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
    return response

@app.route("/prompt", methods=["GET", "POST", "OPTIONS"])
def prompt():
    if request.method=="OPTIONS":
        response=Flask.response_class("no")
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        return response
    global messages
    user_prompt=request.args["prompt"]
    messages.append({"role": "user", "content": user_prompt})
    def handler_full(response):
        global messages
        messages.append({"role":"assistant", "content": response})
    response=flask.Response(llm.proxy_stream(llm.send_message(user_prompt, messages[:len(messages)-1]), full_handle=handler_full), content_type="text/event-stream")
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    return response

@app.get("/new")
def new():
    global messages
    messages=[]
    response=Flask.response_class("true")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.get("/chats")
def chats():
    response=Flask.response_class(json.dumps(messages))
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
    return response

app.run(host="127.0.0.1", port=int(sys.argv[1]))