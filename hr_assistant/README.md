# 🧑‍⚖️ Saudi Labor Law AI Assistant  
### **An intelligent, bilingual HR assistant powered by AI and vector search**

<p align="center">
  <img src="assets/screenshots/chat_example.png" width="85%">
</p>

> ⚡️ *Ask questions, get answers, and understand Saudi labor law — instantly and bilingually.*

---

## 📖 Overview

This project builds an **AI-powered bilingual assistant** that helps HR professionals, employers, and employees understand and apply the **Saudi Labor Law (نظام العمل السعودي)** accurately and efficiently.

It enables users to:

- 💬 **Ask questions** about Saudi labor law in Arabic or English  
- 🧾 **Analyze employee-specific cases**, such as leave eligibility, overtime pay, and service termination  
- 🔍 **Retrieve relevant legal articles** directly from a semantic vector database  
- 🌐 **Support bilingual interaction** — answers in the same language as the question  
- 🧑‍💼 **Integrate employee data dynamically** into the legal reasoning process  

---

## ⚙️ Problem Statement

The Saudi Labor Law is comprehensive and frequently updated, but:  

- The official **English version is outdated**, while the Arabic one is the legal reference.  
- Searching through dozens of pages manually is **time-consuming** and prone to errors.  
- HR professionals need to interpret legal text **contextually** for real employee situations.  

This project solves that problem by combining **document understanding, translation, embeddings, vector search, and LLM reasoning**, to create a system that provides **trustworthy, article-backed answers**.

---

## 📚 Data Source

The assistant uses the **official Saudi Labor Law (Arabic version)** published by the  
**Ministry of Human Resources and Social Development (MHRSD)**.

📄 **Official PDF (Arabic):**  
[https://www.hrsd.gov.sa/sites/default/files/2025-07/nzam-al-ml----wfq-alhwyt-aljdydt-2.pdf](https://www.hrsd.gov.sa/sites/default/files/2025-07/nzam-al-ml----wfq-alhwyt-aljdydt-2.pdf)

---

## 🧩 Data Processing Pipeline

### **1️⃣ PDF Parsing (Arabic Extraction)**

We used **PyMuPDF (fitz)** for robust text extraction from the Arabic PDF.  
Each page was carefully handled to preserve **right-to-left (RTL)** reading order and diacritics.  

Some pages contained complex ligatures and formatting, which were fixed through a custom normalization process.

---

### **2️⃣ Structured Text Splitting**

To build a structured legal database, we split the law into three hierarchical levels:

| Level | Keyword | Example |
|-------|----------|----------|
| **Part** | `الباب` | الباب الرابع – بيئة العمل |
| **Chapter** | `الفصل` | الفصل الرابع – الإجازات |
| **Article** | `المادة` | المادة التاسعة بعد المائة: ... |

We implemented regex-based splitting functions:  

```python
split_parts() → split_chapters() → split_articles()
```

Each article was extracted with metadata like part, chapter, and article number:

```json
{
  "part_title": "أحكام عامة",
  "chapter_title": "الإجازات",
  "article_number_ar": "التاسعة بعد المائة",
  "number": 109,
  "article_content": "يســتحق العامــل..."
}
```

---

### **3️⃣ Translation (Arabic → English)**

Because no up-to-date English version of the law exists, we translated each Arabic article automatically using:

🧠 **Model:** `Helsinki-NLP/opus-mt-ar-en`  

We created two functions:
- `translate_short()` — handles short segments (<512 tokens)
- `translate_long()` — splits long texts intelligently to avoid token truncation  

Each record stores both languages:

```json
{
  "arabic_content": "يســتحق العامــل...",
  "english_content": "The worker is entitled to annual leave..."
}
```

---

## 🧠 Embedding & Vector Database

To enable **semantic search**, we embedded all articles (Arabic + English) using:

📘 **Embedding Model:** `intfloat/multilingual-e5-base`  
🧩 **Vector Store:** `Qdrant` (with cosine similarity)  
⚙️ **Framework:** `LlamaIndex`

Each article and its metadata were converted into vector representations and indexed in Qdrant.

Example setup:

```python
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-base")
vector_store = QdrantVectorStore(client=qdrant, collection_name="hr_company_policies")
```

---

## 🔍 Retrieval & LLM Reasoning

### **Retriever**
- Built using `VectorIndexRetriever` from LlamaIndex  
- Returns the **top 3** semantically similar articles  
- Each result includes **metadata, article text, and similarity score**

### **LLM Reasoning**
The retrieved text is passed to **OpenAI GPT-4o-mini**, which:

- Answers only from the provided context  
- Provides concise, human-readable reasoning  
- Responds in **Arabic or English**, matching the user’s query language  
- Cites relevant articles (e.g., *المادة التاسعة بعد المائة*)  

---

## 🧑‍💼 Employee Data Integration

One of the project’s most powerful features 💪

Users can optionally attach **employee information** when asking a question or analyzing a case.  
This allows the assistant to reason in a **personalized context**, for example:

> “Is this employee eligible for 30 days of annual leave if he has worked for 6 years?”

Collected employee data fields:
- Name  
- Job Title  
- Age  
- Service Years  
- Annual Leave Days Requested  
- Sick Leave Days Requested  
- Basic Wage  
- Total Salary  

If the user checks “Include my employee data,” these fields are appended to the prompt, allowing **contextual legal interpretation** grounded in the employee’s profile.

---

## 💬 Frontend – Streamlit Interface

A clean bilingual web UI was built using **Streamlit**.  

### Features:
- 🌍 **Arabic ↔ English auto-detection**
- 🧾 **Employee Data Form**
- 💬 **Chat interface** for legal questions
- 🧠 **Expandable legal references** (with similarity scores)
- 🧭 **Source tracing:** Part → Chapter → Article
- 🎯 **Accurate bilingual answers**

### Technologies:
| Component | Technology |
|------------|-------------|
| Framework | Streamlit |
| LLM | GPT-4o-mini |
| Embedding | intfloat/multilingual-e5-base |
| Database | Qdrant |
| Indexing | LlamaIndex |
| Translation | Helsinki-NLP/opus-mt-ar-en |
| Text Extraction | PyMuPDF (fitz) |

---

## 🖼️ Application Screenshots

Below are screenshots from the Streamlit interface showcasing the key features of the Saudi Labor Law Assistant.

### 💬 Chat Interface
Ask questions in Arabic or English — the assistant detects the language automatically and answers in the same language.

![Chat Interface](assets/screenshots/chat_example.png)

---

### 👤 Employee Data Form
Users can optionally enter employee details to analyze eligibility for benefits such as annual or sick leave.

![Employee Form](assets/screenshots/employee_form.png)

---

### 📖 Legal Article References
Each answer includes the relevant Part → Chapter → Article, with expandable sections to view the original Arabic text and its English translation.

![Article References](assets/screenshots/article_reference.png)

---

## 🧰 Folder Structure

```
hr_law_bot/
│
├── data/
│   ├── labor_law_ar.pdf      
│   ├── labor_law_parsed.json  # extracted articles 
│
├── process_labor_pdf.py       # PDF Parsing (arabic text extracting,translating , splitting , saved to json)
├── process_data_vectors.py    # Store to Vector DB
├── chatbot_backend.py         # Backend logic (retrieval + reasoning)
├── app.py                     # Streamlit frontend
├── requirements.txt
└── README.md
```

---

## 🚀 Running Locally

```bash
# Clone repo
git clone https://github.com/zainalabdeen/llm-zoomcamp/tree/main/hr_assistant.git
cd hr_assistant

# Install dependencies
pip install -r requirements.txt

# Run Qdrant
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
   -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
   qdrant/qdrant

# Run Streamlit app
streamlit run app.py
```

---

## 🧠 Example Query Flow

**Arabic:**
> المستخدم: ما هي مدة الإجازة السنوية بعد خمس سنوات من الخدمة؟  
> 🤖 المساعد: يستحق العامل ثلاثين يوماً من الإجازة السنوية...  
> 📖 استنادًا إلى المادة التاسعة بعد المائة.

**English:**
> User: What are the sick leave entitlements for an employee?  
> 🤖 Assistant: The employee is entitled to paid sick leave for a specific duration...  
> 📖 Based on Article 117 – Chapter Four.

---

## 🚧 Future Enhancements

- 📑 PDF export of Q&A with referenced articles  
- 🧾 HR calculators (end-of-service, overtime, vacation accrual)  
- 🔊 Arabic voice interaction  
- 📈 Admin dashboard for HR analytics  
- 🧮 Semantic visualization of the law structure  

---

## 🧾 License

This project is open-sourced under the **MIT License**.  
Legal content © **Ministry of Human Resources and Social Development (MHRSD), KSA**.