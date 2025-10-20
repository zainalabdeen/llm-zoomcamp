import os
from typing import List, Dict, Tuple
from dataclasses import dataclass
import pandas as pd

# LlamaIndex core
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Document,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.openai import OpenAI

# Nodes & postprocessors
from llama_index.core.postprocessor import SentenceTransformerRerank

# Qdrant
from qdrant_client import QdrantClient

# BM25
from rank_bm25 import BM25Okapi

# =========================
# CONFIG
# =========================
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "maktek_faqs")
EMBED_MODEL_NAME = "intfloat/multilingual-e5-base"
RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

K = 5  # we’ll evaluate @5 as requested
# knobs
VEC_TOP_K = max(12, K)      # gather more for better recall
BM25_TOP_K = max(12, K)
RERANK_TOP_N = max(8, K)
FINAL_TOP_N = K  

# Optional LLM
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = 0

@dataclass
class CorpusItem:
    doc_id: str
    text: str
    metadata: Dict

# -----------------------------
# DATA LOADING
# -----------------------------
def fetch_maktek_dataset() -> List[Document]:
    #ds = load_dataset("MakTek/Customer_support_faqs_dataset", split="train")
    df = pd.read_json("hf://datasets/MakTek/Customer_support_faqs_dataset/train_expanded.json", lines=True)
    df = df.drop_duplicates(subset="question")
    df.insert(0,'id',df.index)
    df.to_csv("data/data.csv",index=False)
    df_dict = df.to_dict(orient='records')
    docs: List[Document] = []
    for i, row in enumerate(df_dict):
        q = (row.get("question") or "").strip()
        a = (row.get("answer") or "").strip()
        doc_id = f"faq-{i:04d}"
        text = f"Q: {q}\n\nA: {a}"
        metadata = {"question": q, "answer": a, "source": "MakTek", "doc_id": doc_id}
        docs.append(Document(text=text, metadata=metadata, doc_id=doc_id))
    return docs

def load_maktek_dataset(data_path : str = "data/data.csv") -> List[Document]:
    df = pd.read_csv(data_path)
    df_dict = df.to_dict(orient='records')
    docs: List[Document] = []
    for i, row in enumerate(df_dict):
        q = (row.get("question") or "").strip()
        a = (row.get("answer") or "").strip()
        doc_id = f"faq-{i:04d}"
        text = f"Q: {q}\n\nA: {a}"
        metadata = {"question": q, "answer": a, "source": "MakTek", "doc_id": doc_id}
        docs.append(Document(text=text, metadata=metadata, doc_id=doc_id))
    return docs  

# -----------------------------
# INDEX
# -----------------------------
def build_index(docs: List[Document]) -> VectorStoreIndex:
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    client = QdrantClient(url=QDRANT_URL)
    vector_store = QdrantVectorStore(client=client, collection_name=QDRANT_COLLECTION)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context, show_progress=True)
    return index

# --------------------------
# Connect to Qdrant collection
# --------------------------
def connect_to_index() -> VectorStoreIndex:
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    client = QdrantClient(url=QDRANT_URL)
    vector_store = QdrantVectorStore(client=client, collection_name=QDRANT_COLLECTION)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)



#######

def simple_tokenize(s: str) -> List[str]:
    return s.lower().split()


def build_bm25_corpus(docs: List[Document]) -> Tuple[BM25Okapi, Dict[str, CorpusItem]]:
    corpus_items: Dict[str, CorpusItem] = {}
    tokenized_corpus = []
    for d in docs:
        doc_id = d.doc_id or d.metadata.get("doc_id")
        corpus_items[doc_id] = CorpusItem(doc_id=doc_id, text=d.text, metadata=d.metadata)
        tokenized_corpus.append(simple_tokenize(d.text))
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25, corpus_items

# --------------------------
# Reranker builder
# --------------------------
def build_reranker() -> SentenceTransformerRerank:
    return SentenceTransformerRerank(model=RERANK_MODEL_NAME, top_n=RERANK_TOP_N)

def init_store_data_to_vector_db() -> Dict:
    docs = fetch_maktek_dataset()
    index = build_index(docs)
    return index

def prepare_hybird_search(data_path : str = "data/data.csv") -> Dict:
    docs = load_maktek_dataset(data_path)
    index = connect_to_index()
    bm25, corpus_items = build_bm25_corpus(docs)
    return {
    "index": index,
    "bm25": bm25,
    "corpus_items": corpus_items}
