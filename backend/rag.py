import os
import json
import numpy as np
import google.generativeai as genai
from pypdf import PdfReader
import config

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
KNOWLEDGE_DIR = os.path.join(ROOT_DIR, "knowledge")
PDF_PATH = os.path.join(KNOWLEDGE_DIR, "memory.pdf")
INDEX_PATH = os.path.join(KNOWLEDGE_DIR, "knowledge_index.json")

def initialize_rag():
    """Reads PDF, chunks it, and creates an embedding index."""
    if not os.path.exists(PDF_PATH):
        print(f"!! PDF Not Found at {PDF_PATH}")
        return

    print(f"[RAG] Indexing {PDF_PATH}...")
    
    # 1. Extract Text
    reader = PdfReader(PDF_PATH)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # 2. Chunking (Simple overlap chunking)
    chunks = []
    lines = text.split("\n")
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) < 1000:
            current_chunk += line + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())

    # 3. Embed & Save
    genai.configure(api_key=config.GEMINI_API_KEY)
    embeddings_data = []
    
    for chunk in chunks:
        if not chunk: continue
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=chunk,
                task_type="retrieval_query"
            )
            embeddings_data.append({
                "chunk": chunk,
                "embedding": result['embedding']
            })
        except Exception as e:
            print(f"!! Embedding Error: {e}")

    with open(INDEX_PATH, "w") as f:
        json.dump(embeddings_data, f)
    
    print(f"[RAG] Index created with {len(embeddings_data)} chunks.")

def search_knowledge(query):
    """Searches the local index for the most relevant chunk."""
    if not os.path.exists(INDEX_PATH):
        initialize_rag()
    
    if not os.path.exists(INDEX_PATH):
        return "Knowledge base is currently unavailable."

    with open(INDEX_PATH, "r") as f:
        data = json.load(f)

    # 1. Embed Query
    genai.configure(api_key=config.GEMINI_API_KEY)
    try:
        query_embedding = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )['embedding']
    except:
        return ""

    # 2. Simple Cosine Similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    best_chunk = ""
    best_score = -1
    
    for item in data:
        score = cosine_similarity(query_embedding, item['embedding'])
        if score > best_score:
            best_score = score
            best_chunk = item['chunk']

    print(f"  <- RAG Match (Score: {best_score:.2f})")
    # Return top chunk if score is decent
    return best_chunk if best_score > 0.4 else ""

if __name__ == "__main__":
    initialize_rag()
