# frontend/app.py
import sys,os
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🔧 Import backend services
from backend import rag_service, feedback_service

# ----------------------------
# ⚙️ Streamlit Page Config
# ----------------------------
st.set_page_config(
    page_title="📚 Customer Support FAQ Search",
    page_icon="🔎",
    layout="wide"
)
st.title("📚 Customer Support FAQ Search")

# ----------------------------
# 🔌 Connect to Qdrant Index
# ----------------------------
st.sidebar.header("⚙️ Settings")
use_llm = st.sidebar.toggle("Use OpenAI LLM for final answer", value=False)

st.sidebar.info("💡 You can turn off the LLM to see raw retrieval results.")

# Connect to vector DB
st.sidebar.write("🔗 Connecting to Qdrant...")
prepared_dict = rag_service.connect_to_qdrant()
st.sidebar.success("✅ Connected to Qdrant successfully!")

# ----------------------------
# 🔍 Query Input
# ----------------------------
query = st.text_input(
    "🔍 Ask a question:",
    placeholder="e.g. How do I reset my password?"
)
submitted = None
# ----------------------------
# 🔎 Search Button
# ----------------------------
if st.button("Search"):
    if not query.strip():
        st.warning("⚠️ Please enter a question before searching.")
        st.stop()

    with st.spinner("🔍 Retrieving results..."):
        # Retrieve results (without LLM)
        results = rag_service.retrieve_answers(query,prepared_dict)

    st.subheader("📊 Retrieved Results")
    for i, r in enumerate(results, 1):
        with st.expander(f"{i}. {r['question']} (Score: {r['score']:.4f})"):
            st.write(f"**Answer:** {r['answer']}")
            st.caption(f"Doc ID: `{r['doc_id']}`")

    # ----------------------------
    # 🤖 LLM Answer (Optional)
    # ----------------------------
    llm_answer = None
    if use_llm:
        if not os.getenv("OPENAI_API_KEY"):
            st.error("⚠️ OPENAI_API_KEY is not set. Cannot run LLM answer.")
        else:
            with st.spinner("🤖 Generating final answer with OpenAI..."):
                llm_answer = rag_service.generate_final_answer(query, results)

            st.subheader("🤖 Final LLM Answer")
            st.write(llm_answer["answer"])

            with st.expander("📚 Context used by LLM"):
                for i, ctx in enumerate(llm_answer["top_context"], 1):
                    st.markdown(f"**{i}.** Q: {ctx['question']}\n\nA: {ctx['answer']}")

    # ----------------------------
    # 💬 Feedback Form
    # ----------------------------
    st.subheader("💬 Provide Feedback on This Answer")

    # Store answer used for feedback (LLM answer if used, otherwise retrieved one)
    final_answer = llm_answer["answer"] if use_llm and llm_answer else results[0]["answer"]

    with st.form("feedback_form", clear_on_submit=True):
        feedback_text = st.text_area(
            "Your feedback:",
            placeholder="Was the answer helpful? What could be improved?"
        )
        rating = st.select_slider(
            "How satisfied are you with the answer?",
            options=[1, 2, 3, 4, 5],
            value=3
        )
        submitted = st.form_submit_button("✅ Submit Feedback")

    if submitted:
        try:
            feedback_service.save_feedback(
                query=query,
                answer=final_answer,
                feedback=feedback_text,
                rating=rating
            )
            st.success("🎉 Thank you! Your feedback has been recorded.")
        except Exception as e:
            st.error(f"❌ Failed to save feedback: {e}")
