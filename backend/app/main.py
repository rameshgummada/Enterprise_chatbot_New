from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

from app.config import API_KEY
from app.confluence_client import ConfluenceClient

client = genai.Client(api_key=API_KEY)
confluence = ConfluenceClient()

app = FastAPI(title="Enterprise Chatbot API")

class ChatRequest(BaseModel):
    message: str
    user: str

@app.post("/chat")
def chat(req: ChatRequest):
    pages = confluence.search_pages(req.message, limit=8)

    enriched = []
    for page in pages[:5]:
        try:
            content = confluence.get_page_content(page["id"])
            enriched.append({
                "title": page["title"],
                "url": page["url"],
                "snippet": page["snippet"],
                "content": content["html"][:4000]
            })
        except Exception:
            enriched.append({
                "title": page["title"],
                "url": page["url"],
                "snippet": page["snippet"],
                "content": ""
            })

    context = "\n\n".join(
        f"Title: {p['title']}\nURL: {p['url']}\nSnippet: {p['snippet']}\nContent: {p['content']}"
        for p in enriched
    )

    prompt = f"""
You are an enterprise assistant.
Answer the user's question using only the Confluence context below.
If the answer is uncertain, say so clearly.
Also summarize the most relevant policy/process points in a practical way.

Context:
{context}

User question:
{req.message}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return {
        "reply": response.text,
        "sources": [
            {"title": p["title"], "url": p["url"], "snippet": p["snippet"]}
            for p in pages
        ]
    }


# from fastapi import FastAPI
# from pydantic import BaseModel
# from google import genai

# from app.rag_engine import RAGEngine
# from app.faq_loader import load_faq
# from app.config import API_KEY
# from fastapi.middleware.cors import CORSMiddleware

# client = genai.Client(api_key=API_KEY)

# docs = load_faq()
# rag = RAGEngine()
# rag.add_docs(docs)

# app = FastAPI(title="Enterprise Chatbot API")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



# class ChatRequest(BaseModel):
#     message: str
#     user: str


# @app.get("/healthz")
# def healthz():
#     return {"status": "ok"}


# @app.post("/chat")
# def chat(req: ChatRequest):
#     context_docs = rag.search(req.message)
#     context_text = "\n\n".join(
#         [f"Q: {d['question']}\nA: {d['answer']}" for d in context_docs]
#     )

#     prompt = f"""
# You are a helpful assistant. Answer the question only using the following context.

# Context:
# {context_text}

# User question:
# {req.message}
# """

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt,
#     )

#     return {"reply": response.text}