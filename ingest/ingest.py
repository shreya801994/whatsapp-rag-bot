import sys
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

CHROMA_HOST = "chromadb"
CHROMA_PORT = 8000
COLLECTION_NAME = "my_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"

def ingest(pdf_path: str):
    print(f"Loading {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=60,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(pages)
    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata for c in chunks]
    print(f"Split into {len(texts)} chunks.")

    print("Embedding chunks...")
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    print("Storing in ChromaDB...")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    ids = [f"chunk_{i}" for i in range(len(texts))]
    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    print(f"Done. {len(texts)} chunks stored in collection '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/docs/document.pdf"
    ingest(path)
