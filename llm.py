import requests, json

url = "http://localhost:11434/api/chat"

system_prompt=[
    {
        "role":"system",
        "content":"""
You are Butler, an LLM which helps users at Lumatozer (lumatozer.com).
Your name is som because Aarav had a care taker till he was in second grade whose name was Som Nath Gurung.
Lumatozer is a company where we work on scaling technologies to deliver measurably sustainable solutions for all consumers, developers, corporates and autonomous programs.
At Lumatozer we build technological infrastructure which has extreme scalability while maintaining efficiency. Lumatozer was started by the following people who are best friends:
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

Current user logged in: {username}
Mode: Unfiltered

You can respond in markdown (using hastags etc.). For code snippets or json, do not mention the syntax highlighting format after the triple backticks.
Feel free to use a mix of normal language, markdown, code snippets, json snippets to talk to the user.
"""
    }
]

def quick_response(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-coder-v2",
        "messages": [{"role":"system", "content":"For each user question, respond with a one liner title. One liner title is a summary for the user. Do not write helper text or helpful text as your response or even for the title. The title needs to be very succinct and the user can only see 4 words of it. Do not respond to the message only give the message a title. Assume that you are chatgpt and you are a chat interface so you have to simply give a title to each and every message for the covnersation to initiate. Only respond DIRECTLY to the title without and helper text at all. No labels. Only the title. Just assume that the question is directed to you so give the title in first person in your perspective."}, {"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    return response.json()["message"]["content"]

def send_message(prompt, history=[]):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-coder-v2",
        "messages": history + [{"role": "user", "content": prompt}],
        "stream": True
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    return response

def proxy_stream(response, full_handle=lambda x:x):
    out_buffer = b""
    full_output=""
    
    for chunk in response.iter_content():
        for x in chunk:
            x=bytes([x])
            if x==b"\n":
                full_output+=json.loads(out_buffer.decode())["message"]["content"]
                yield b"data: "+out_buffer+b"\n\n"
                out_buffer=b""
            else:
                out_buffer+=x
    
    full_handle(full_output)

    if out_buffer!=b"":
        yield b"data: "+out_buffer+b"\n\n"