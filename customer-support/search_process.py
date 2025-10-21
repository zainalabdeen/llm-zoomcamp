import os
from typing import List, Dict, Tuple
from llama_index.core import (
    VectorStoreIndex
)
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import TextNode, NodeWithScore
from rank_bm25 import BM25Okapi
from data_ingestion import prepare_hybird_search , simple_tokenize , CorpusItem , build_reranker

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


 

# -----------------------------
# RETRIEVAL HELPERS
# -----------------------------
def as_results(nodes: List[NodeWithScore]) -> List[Dict]:
    """Convert NodeWithScore → dict rows."""
    out = []
    for n in nodes[:FINAL_TOP_N]:
        out.append({
            "doc_id": n.metadata.get("doc_id") if n.metadata else n.node.node_id,
            "question": n.metadata.get("question", ""),
            "answer": n.metadata.get("answer", ""),
            "score": float(n.score or 0.0),
        })
    return out

def dedup_exact_question(rows: List[Dict]) -> List[Dict]:
    """Keep only the first instance of identical question text (case-insensitive)."""
    seen = set()
    uniq = []
    for r in rows:
        key = (r.get("question") or "").strip().lower()
        if key not in seen:
            seen.add(key)
            uniq.append(r)
        if len(uniq) >= FINAL_TOP_N:
            break
    return uniq


def retrieve_hybrid_rerank(index: VectorStoreIndex, bm25: BM25Okapi, corpus: Dict[str, CorpusItem], query: str) -> List[Dict]:
    # stage 1: gather candidates (same as hybrid)
    v_nodes = index.as_retriever(similarity_top_k=VEC_TOP_K).retrieve(query)

    scores = bm25.get_scores(simple_tokenize(query))
    doc_ids = list(corpus.keys())
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:BM25_TOP_K]
    b_nodes: List[NodeWithScore] = []
    for idx, sc in ranked:
        did = doc_ids[idx]
        item = corpus[did]
        b_nodes.append(NodeWithScore(node=TextNode(id_=did, text=item.text, metadata=item.metadata), score=float(sc)))

    # merge by doc_id
    merged: Dict[str, NodeWithScore] = {}
    for n in v_nodes + b_nodes:
        did = n.metadata.get("doc_id") if n.metadata else n.node.node_id
        if did not in merged or (merged[did].score or 0) < (n.score or 0):
            merged[did] = n

    # stage 2: rerank with cross-encoder
    reranker = build_reranker()
    reranked = reranker.postprocess_nodes(list(merged.values()), query_str=query)

    rows = as_results(reranked)
    return dedup_exact_question(rows)

# --------------------------
# Query (Retrieval Only)
# --------------------------
def query_without_llm(index: VectorStoreIndex,bm25: BM25Okapi, corpus: Dict[str, CorpusItem], query: str) -> List[Dict]:
    result = retrieve_hybrid_rerank(index, bm25, corpus, query)
    return result


# --------------------------
# Query (With LLM)
# --------------------------
def query_with_llm(query: str , vector_result:List[Dict] ,model : str ="gpt-3.5-turbo") -> Dict:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")
    context_text = "\n\n".join([f"[{i+1}] Q: {r['question']}\nA: {r['answer']}" for i, r in enumerate(vector_result)])

    prompt = f"""You are a helpful support assistant. Answer the user's question using ONLY the context below.
If the answer is not present, say you don't have enough information.

User question:
{query}

Context:
{context_text}

Return a concise, direct answer.
"""

    llm = OpenAI(model=model, temperature=0)
    completion = llm.complete(prompt)

    return {
        "query": query,
        "answer": completion.text.strip(),
        "top_context": vector_result
    }

def prepare_search(data_path : str = "data/data.csv") -> Dict:
    result = prepare_hybird_search(data_path)
    return result

def do_search(query: str , prepare_dict : Dict, model : str ="gpt-3.5-turbo") -> Dict:
    vector_result = query_without_llm(prepare_dict['index'],prepare_dict['bm25'],prepare_dict['corpus_items'], query)
    result = query_with_llm(query,vector_result,model)
    return result

def test_query(prepare_dict, query: str):
    results = query_without_llm(
        prepare_dict['index'],
        prepare_dict['bm25'],
        prepare_dict['corpus_items'],
        query
    )
    print("🔍 Query:", query)
    for r in results:
        print(f" - {r['question']}  (score={r['score']:.4f})")



