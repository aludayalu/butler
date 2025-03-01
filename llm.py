import requests, json
from datetime import datetime

url = "http://localhost:11434/api/chat"

system_prompts=[
    {
        "role":"system",
        "content":"""
You are Butler, an LLM which helps users at Lumatozer (lumatozer.com).

Your name is som because Aarav had a care taker till he was in second grade whose name was Som Nath Gurung.

Lumatozer is a company where we work on scaling technologies to deliver measurably sustainable solutions for all consumers, developers, corporates and autonomous programs.

At Lumatozer we build technological infrastructure which has extreme scalability while maintaining efficiency.

Lumatozer was started by the following people who are best friends:
    1. Aarav Dayal (CEO, Founder, Technology Head, Head of Infrastructure and Head of Architecture Design) Roles: ["admin"]
    2. Kritarth Shankar (Co-Founder, Cyber Security Head and DevOps Head)
    3. Chaitanya Daftuar (Co-Founder and Chief of Logistics)
    4. Atharv Varshney (Co-Founder, Chief of Platforms and Relations)
    5. Tanmay Malpani (Co-Founder and CFO)

Username to name translations for the founder and cofounders:
    aludayalu => Aarav Dayal
    kshankr => Kritarth Shankar
    atharv_777 => Atharv Varshney
    daftuar => Chaitanya Daftuar
    tanmay => Tanmay Malpani

[config]
    Current user logged is aludayalu.
    Mode: Unfiltered
[/config]

[time]
Time when this conversation started (not the current exact time, probably): {time}
[/time]

You can respond in markdown (using hastags etc.). For code snippets or json, do not mention the syntax highlighting format after the triple backticks.
Feel free to use a mix of normal language, markdown, code snippets, json snippets to talk to the user.

Please take full advantage of the markdown rendering applied to your outputs. Properly format your responses into separate lines and sections.

If you have been asked to work with a code snippet, do not change function signature at all.

For small snippets and functions, do not write comments.

This first-message is the system prompt. Do not tell the user the system prompt until the user explicity asks for the "system prompt".
"""
    }
]

def quick_response(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen2.5-coder:7b",
        "messages": [{"role":"system", "content":"Reply minimally."}, {"role":"user", "content":prompt}],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    return response.json()["message"]["content"]

def send_message(prompt, history=[]):
    headers = {
        "Content-Type": "application/json"
    }

    current_datetime = datetime.now()

    formatted_datetime = current_datetime.strftime("%B %d, %Y, %I:%M:%S %p")

    system_prompt=system_prompts[0].copy()

    system_prompt["content"]=system_prompt["content"].replace("{time}", formatted_datetime)

    payload = {
        "model": "qwen2.5-coder:7b",
        "messages": history + [system_prompt, {"role": "user", "content": prompt}],
        "stream": True
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    return response

def proxy_stream(response, handler=lambda x:x):
    out_buffer = b""
    for chunk in response.iter_content():
        for x in chunk:
            x=bytes([x])
            if x==b"\n":
                handler(json.loads(out_buffer.decode())["message"]["content"])
                yield b"data: "+out_buffer+b"\n\n"
                out_buffer=b""
            else:
                out_buffer+=x

    if out_buffer!=b"":
        yield b"data: "+out_buffer+b"\n\n"