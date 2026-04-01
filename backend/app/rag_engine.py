
from google import genai
import numpy as np
from app.config import API_KEY


class RAGEngine:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)
        self.docs = []
        self.vectors = []

    def _embed_text(self, text: str):
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return np.array(response.embeddings[0].values)

    def add_docs(self, docs):
        self.docs = docs
        self.vectors = [self._embed_text(d["question"]) for d in docs]

    def search(self, query, top_k=3):
        q_emb = self._embed_text(query)
        scores = [float(np.dot(q_emb, v)) for v in self.vectors]
        idx = np.argsort(scores)[-top_k:][::-1]
        return [self.docs[i] for i in idx]