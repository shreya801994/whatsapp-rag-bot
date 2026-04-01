import requests
import chromadb
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

CHROMA_HOST = "chromadb"
CHROMA_PORT = 8000
COLLECTION_NAME = "my_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"

embedder = SentenceTransformer(EMBED_MODEL)
chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

def ingest_from_url(media_url: str, account_sid: str, auth_token: str):
    # Download PDF from Twilio (requires auth)
    response = requests.get(media_url, auth=(account_sid, auth_token))
    response.raise_for_status()

    # Save to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(response.content)
        tmp_path = f.name

    try:
        # Load and chunk
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=60
        )
        chunks = splitter.split_documents(pages)
        texts = [c.page_content for c in chunks]

        # Embed
        embeddings = embedder.encode(texts).tolist()

        # Store in ChromaDB — clear old data first
        try:
            chroma.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

        collection = chroma.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        ids = [f"chunk_{i}" for i in range(len(texts))]
        collection.add(ids=ids, documents=texts, embeddings=embeddings)

    finally:
        os.unlink(tmp_path)  # clean up temp file