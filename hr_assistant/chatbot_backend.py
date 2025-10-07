from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import Settings ,StorageContext, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from qdrant_client import QdrantClient
from openai import OpenAI
import re
# ---------- CONFIG ----------
QDRANT_URL = "http://localhost:6333"
COLLECTION = "saudi_labor_law"
EMBED_MODEL = "intfloat/multilingual-e5-base"

client = OpenAI()

# ---------- Embedding Model ----------
embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
Settings.embed_model = embed_model


# ---------- Utility ----------
def detect_language(text: str) -> str:
    """Detect if the question is Arabic or English."""
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    return "ar" if arabic_chars > len(text) / 2 else "en"
def highlight_articles(text: str):
    return re.sub(r"(المادة\s+[^\s،.]+|Article\s+\d+)", r"**\1**", text)
# ---------- Qdrant Retriever ----------
def get_retriever():
    qdrant = QdrantClient(url=QDRANT_URL)
    store = QdrantVectorStore(client=qdrant, collection_name=COLLECTION)
    vector_store = QdrantVectorStore(client=qdrant, collection_name=COLLECTION)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context,
    embed_model=embed_model)
    retriever = VectorIndexRetriever(
        index=index,
        vector_store=store,
        embed_model=embed_model,
        similarity_top_k=3
    )
    return retriever

# ---------- Chatbot ----------

# ---------- Core Answer Function ----------
def generate_answer(query: str, context: str, lang: str) -> str:
    """Call LLM with language-specific instructions."""
    if lang == "ar":
        prompt = f"""أنت مساعد ذكي متخصص في نظام العمل السعودي.
اعتمد فقط على النصوص أدناه للإجابة على السؤال بدقة وبالعربية:

النصوص ذات الصلة:
{context}

السؤال: {query}

الإجابة:"""
    else:
        prompt = f"""You are an intelligent assistant specialized in Saudi Labor Law.
Use **only** the following text to answer the question accurately in English:

Relevant Articles:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content.strip()
    return highlight_articles(answer)

# ---------- Public API ----------
def answer_policy_question(query: str, employee_data: dict | None = None):
    """Answer a policy question, optionally enriched with employee data."""
    retriever = get_retriever()
    lang = detect_language(query)

    # If user chose to include employee data
    if employee_data:
        employee_info = (
            f"\n\nEmployee Info:\n"
            f"Name: {employee_data['name']}\n"
            f"Job: {employee_data['job']}\n"
            f"Age: {employee_data['age']}\n"
            f"Service Years: {employee_data['service_years']}\n"
            f"Annual Leave: {employee_data['annual_leave_days']}\n"
            f"Sick Leave: {employee_data['sick_leave_days']}\n"
            f"Basic Wage: {employee_data['basic_wage']}\n"
            f"Total Salary: {employee_data['total_salary']}\n"
        )
        query += employee_info

    results = retriever.retrieve(query)
    if not results:
        return "❌ لم يتم العثور على مواد ذات صلة." if lang == "ar" else "❌ No relevant articles found.", []

    context = "\n\n".join([r.node.get_content() for r in results])
    answer = generate_answer(query, context, lang)

    references = []
    for r in results:
        meta = r.node.metadata
        references.append({
            "similarity": round(r.score, 3),
            "part": meta.get("part_title_ar", ""),
            "chapter": meta.get("chapter_title_ar", ""),
            "article_name": meta.get("arabic_name", "غير معروفة"),
            "article_number": meta.get("number_ar", ""),
            "arabic_content": meta.get("arabic_content", ""),
            "english_content": meta.get("english_content", "")
        })

    return answer, references