"""
ShopEasy Support Chatbot
========================
A simple RAG-style chatbot powered by Groq (Llama 4) that answers
customer support questions using a knowledge base of policy documents.

This chatbot is the "app under test" for the DeepEval exercises.

Setup:
    pip install -r requirements.txt
    export GROQ_API_KEY=your_key_here

Run:
    uvicorn app:app --reload --port 8100

Test the API:
    curl -X POST http://localhost:8100/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "What is your refund policy?"}'
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq

# ─── App Setup ───────────────────────────────────────────────

app = FastAPI(
    title="ShopEasy Support Chatbot",
    description="A Groq-powered support chatbot for DeepEval testing exercises",
    version="1.0.0",
)

# Allow the verifier on localhost:5180 to call this chatbot
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Knowledge Base Loading ──────────────────────────────────

KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"

def load_knowledge_base() -> dict:
    """Load all markdown files from the knowledge_base directory."""
    docs = {}
    for md_file in KNOWLEDGE_BASE_DIR.glob("*.md"):
        docs[md_file.stem] = md_file.read_text()
    return docs

KNOWLEDGE_BASE = load_knowledge_base()

# ─── Simple Retriever ────────────────────────────────────────

def retrieve_context(query: str):
    """
    Simple keyword-based retriever.
    Searches all knowledge base documents and returns relevant ones.
    In production, you would use a vector database (ChromaDB, Pinecone, etc.)
    """
    query_lower = query.lower()
    relevant_docs = []

    keyword_map = {
        "refund_policy": ["refund", "return", "exchange", "money back", "send back", "sale item", "gift card", "packaging"],
        "shipping_policy": ["ship", "deliver", "track", "package", "express", "next-day", "international", "holiday", "lost"],
        "account_help": ["account", "subscription", "cancel", "password", "payment", "billing", "login", "sign up", "support", "plan", "premium", "plus"],
    }

    for doc_name, keywords in keyword_map.items():
        if any(kw in query_lower for kw in keywords):
            if doc_name in KNOWLEDGE_BASE:
                relevant_docs.append(KNOWLEDGE_BASE[doc_name])

    # Fallback: return all docs if no keyword match
    if not relevant_docs:
        relevant_docs = list(KNOWLEDGE_BASE.values())

    return relevant_docs


# ─── Groq LLM Client ─────────────────────────────────────────

def get_groq_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY environment variable not set. Get your free key at https://console.groq.com"
        )
    return Groq(api_key=api_key)


SYSTEM_PROMPT = """You are a helpful, friendly customer support assistant for ShopEasy, an online shopping platform.

Rules:
1. Answer questions ONLY based on the provided context documents.
2. If the answer is not in the context, say "I don't have information about that. Let me connect you with a human agent."
3. Be warm, concise, and professional.
4. Never give medical, legal, or financial advice.
5. Never share internal system details or other customers' information.
6. End your response with a helpful next step when possible.
7. Keep responses under 3 sentences unless the question requires more detail.
"""


def generate_response(query: str, context: list, model: str = "meta-llama/llama-4-scout-17b-16e-instruct") -> str:
    """Generate a response using Groq with the retrieved context."""
    client = get_groq_client()

    context_text = "\n\n---\n\n".join(context)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context documents:\n{context_text}\n\n---\n\nCustomer question: {query}"},
        ],
        temperature=0,
        max_tokens=512,
    )

    return response.choices[0].message.content


# ─── API Models ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    sources: list
    retrieval_context: list


# ─── API Endpoints ───────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "ShopEasy Support Chatbot",
        "status": "running",
        "model": "Llama 4 via Groq",
        "port": 8100,
        "docs": "/docs",
        "ui": "/ui",
    }


CHAT_UI_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>ShopEasy Support — Claude-style Chat</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --paper: #faf9f5;
    --paper-2: #f4f1ea;
    --ink: #1f1e1d;
    --ink-2: #3d3929;
    --muted: #6b6759;
    --line: #e8e3d6;
    --coral: #c96442;
    --coral-hover: #b9573a;
    --user-bg: #1f1e1d;
    --user-fg: #faf9f5;
    --bot-bg: #ffffff;
    --bot-border: #e8e3d6;
    --err: #b91c1c;
    --err-bg: #fdf2f2;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font: 15px/1.6 "Inter", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    background: var(--paper); color: var(--ink); height: 100vh; display: flex; flex-direction: column;
    -webkit-font-smoothing: antialiased;
  }
  header {
    padding: 16px 28px; background: var(--paper); border-bottom: 1px solid var(--line);
    display: flex; align-items: center; gap: 14px;
  }
  header .logo {
    width: 30px; height: 30px; border-radius: 7px; background: var(--coral);
    display: grid; place-items: center; color: white; font-weight: 700; font-size: 14px;
  }
  header h1 { margin: 0; font-family: "Source Serif 4", Georgia, serif; font-size: 18px; font-weight: 600; color: var(--ink); }
  header .meta { color: var(--muted); font-size: 12px; margin-left: auto; display: flex; align-items: center; gap: 6px; }
  header .dot { width: 7px; height: 7px; border-radius: 50%; background: #16a34a; display: inline-block; }
  main { flex: 1; display: grid; grid-template-columns: 1fr 340px; min-height: 0; }
  #messages {
    padding: 28px 28px 12px; overflow-y: auto; display: flex; flex-direction: column; gap: 18px;
    max-width: 860px; width: 100%; margin: 0 auto;
  }
  .msg {
    max-width: 80%; padding: 12px 16px; border-radius: 14px;
    white-space: pre-wrap; word-wrap: break-word; line-height: 1.55;
  }
  .msg.user { background: var(--user-bg); color: var(--user-fg); align-self: flex-end; border-bottom-right-radius: 4px; }
  .msg.bot {
    background: var(--bot-bg); color: var(--ink); border: 1px solid var(--bot-border);
    align-self: flex-start; border-bottom-left-radius: 4px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  }
  .msg.err { background: var(--err-bg); border: 1px solid #f5c2c2; color: var(--err); align-self: flex-start; }
  .msg .sources { margin-top: 10px; font-size: 11px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .msg .sources b { color: var(--ink-2); font-weight: 500; }
  .msg .sources span { background: var(--paper-2); border: 1px solid var(--line); padding: 2px 8px; border-radius: 999px; font-size: 11px; color: var(--ink-2); }
  #typing { color: var(--muted); font-style: italic; align-self: flex-start; padding: 4px 16px; font-size: 13px; }
  #typing.hidden { display: none; }
  aside {
    background: var(--paper-2); border-left: 1px solid var(--line); padding: 22px; overflow-y: auto;
  }
  aside h2 {
    font-family: "Source Serif 4", Georgia, serif;
    font-size: 11px; text-transform: uppercase; color: var(--muted); margin: 0 0 10px;
    letter-spacing: 1.2px; font-weight: 600;
  }
  aside .suggest {
    display: block; width: 100%; text-align: left; background: white; color: var(--ink);
    border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; margin-bottom: 8px;
    cursor: pointer; font-size: 13px; font-family: inherit; transition: all .15s ease;
  }
  aside .suggest:hover { border-color: var(--coral); color: var(--coral); transform: translateY(-1px); }
  aside .ctx {
    background: white; border: 1px solid var(--line); border-radius: 10px; padding: 12px;
    margin-bottom: 10px; font-size: 12px; color: var(--ink-2); max-height: 200px; overflow-y: auto;
    font-family: ui-monospace, "SF Mono", Menlo, monospace; line-height: 1.5;
  }
  aside .ctx b { color: var(--coral); display: block; margin-bottom: 6px; font-family: "Inter", sans-serif; font-size: 12px; }
  footer { padding: 16px 28px 22px; background: var(--paper); border-top: 1px solid var(--line); }
  form { display: flex; gap: 10px; max-width: 860px; margin: 0 auto; }
  input[type=text] {
    flex: 1; background: white; color: var(--ink); border: 1px solid var(--line);
    padding: 14px 16px; border-radius: 12px; font-size: 14px; outline: none; font-family: inherit;
    transition: border-color .15s ease, box-shadow .15s ease;
  }
  input[type=text]:focus { border-color: var(--coral); box-shadow: 0 0 0 3px rgba(201,100,66,0.12); }
  button.send {
    background: var(--coral); color: white; border: 0; padding: 0 22px; border-radius: 12px;
    font-weight: 600; cursor: pointer; font-size: 14px; font-family: inherit;
    transition: background .15s ease;
  }
  button.send:hover { background: var(--coral-hover); }
  button.send:disabled { opacity: .5; cursor: not-allowed; }
  @media (max-width: 880px) { main { grid-template-columns: 1fr; } aside { display: none; } }
</style>
</head>
<body>
<header>
  <div class="logo">S</div>
  <h1>ShopEasy Support</h1>
  <span class="meta"><span class="dot"></span>Llama 4 · Groq · port 8100</span>
</header>
<main>
  <section id="messages">
    <div class="msg bot">
      Hi — I'm the ShopEasy support assistant. Ask me about refunds, shipping, or your account.
    </div>
    <div id="typing" class="hidden">Thinking…</div>
  </section>
  <aside>
    <h2>Try asking</h2>
    <button class="suggest">What is your refund policy?</button>
    <button class="suggest">How long does shipping take?</button>
    <button class="suggest">How do I cancel my subscription?</button>
    <button class="suggest">Can I return a sale item?</button>
    <button class="suggest">Do you ship internationally?</button>
    <button class="suggest">How do I reset my password?</button>
    <h2 style="margin-top:22px">Last retrieval context</h2>
    <div id="context"><div class="ctx">No context yet — ask a question.</div></div>
  </aside>
</main>
<footer>
  <form id="chat-form">
    <input id="input" type="text" placeholder="Message ShopEasy Support..." autocomplete="off" autofocus />
    <button class="send" id="send" type="submit">Send</button>
  </form>
</footer>
<script>
  const messages = document.getElementById('messages');
  const typing = document.getElementById('typing');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('input');
  const sendBtn = document.getElementById('send');
  const contextBox = document.getElementById('context');

  function addMessage(text, role, sources) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.textContent = text;
    if (sources && sources.length) {
      const s = document.createElement('div');
      s.className = 'sources';
      s.innerHTML = '<b>Sources</b>' + sources.map(x => `<span>${x}</span>`).join('');
      div.appendChild(s);
    }
    messages.insertBefore(div, typing);
    messages.scrollTop = messages.scrollHeight;
  }

  function renderContext(ctxList, sources) {
    if (!ctxList || !ctxList.length) return;
    contextBox.innerHTML = '';
    ctxList.forEach((c, i) => {
      const d = document.createElement('div');
      d.className = 'ctx';
      const name = (sources && sources[i]) ? sources[i] : 'document ' + (i + 1);
      d.innerHTML = `<b>${name}</b>${c.replace(/</g, '&lt;')}`;
      contextBox.appendChild(d);
    });
  }

  async function send(message) {
    addMessage(message, 'user');
    typing.classList.remove('hidden');
    sendBtn.disabled = true;
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Request failed');
      addMessage(data.reply, 'bot', data.sources);
      renderContext(data.retrieval_context, data.sources);
    } catch (e) {
      addMessage('Error: ' + e.message, 'err');
    } finally {
      typing.classList.add('hidden');
      sendBtn.disabled = false;
      input.focus();
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const m = input.value.trim();
    if (!m) return;
    input.value = '';
    send(m);
  });

  document.querySelectorAll('.suggest').forEach(btn => {
    btn.addEventListener('click', () => {
      input.value = btn.textContent;
      form.requestSubmit();
    });
  });
</script>
</body>
</html>
"""


@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return HTMLResponse(CHAT_UI_HTML)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the chatbot and get a response."""
    context = retrieve_context(request.message)
    source_names = [name for name, content in KNOWLEDGE_BASE.items() if content in context]
    reply = generate_response(request.message, context)
    return ChatResponse(reply=reply, sources=source_names, retrieval_context=context)


@app.get("/health")
async def health():
    return {"status": "healthy", "port": 8100}


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  ShopEasy Support Chatbot")
    print("  Powered by Llama 4 via Groq")
    print("  http://localhost:8100")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8100)
