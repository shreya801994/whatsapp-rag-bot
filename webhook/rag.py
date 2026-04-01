import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer

OLLAMA_URL = "http://ollama:11434/api/generate"
CHROMA_HOST = "chromadb"
CHROMA_PORT = 8000
COLLECTION_NAME = "my_docs"
MODEL_NAME = "mistral"
EMBED_MODEL = "all-MiniLM-L6-v2"

embedder = SentenceTransformer(EMBED_MODEL)
chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

def query_rag(question: str, top_k: int = 3) -> str:
    # 1. Embed the question
    q_vec = embedder.encode([question]).tolist()

    # 2. Retrieve top-k relevant chunks from ChromaDB
    try:
        collection = chroma.get_collection(COLLECTION_NAME)
        results = collection.query(query_embeddings=q_vec, n_results=top_k)
        chunks = results["documents"][0]
    except Exception:
        return "No document has been ingested yet. Please upload a PDF first."

    # 3. Build prompt with retrieved context
    context = "\n\n".join(chunks)
    prompt = f"""You are a helpful assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I couldn't find that in the document."

Context:
{context}

Question: {question}
Answer:"""

    # 4. Call local Ollama LLM
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }, timeout=300)
        return response.json().get("response", "Sorry, I couldn't generate a response.")
    except Exception as e:
        return f"LLM error: {str(e)}"
