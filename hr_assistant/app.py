import streamlit as st
from chatbot_backend import answer_policy_question

st.set_page_config(page_title="Saudi Labor Law Assistant", layout="wide")

# ---------- Sidebar ----------
st.sidebar.header("🌐 Language / اللغة")
language = st.sidebar.radio("Choose Language / اختر اللغة:", ["English", "العربية"])

st.title("🧑‍⚖️ Saudi Labor Law Assistant" if language == "English" else "🧑‍⚖️ المساعد الذكي لنظام العمل السعودي")

tab1, tab2 = st.tabs(
    ["💬 ChatBot" if language == "English" else "💬 المحادثة",
     "👤 Employee Info" if language == "English" else "👤 بيانات الموظف"]
)

# ------------------------------------------------------------
# 💬 CHAT TAB
# ------------------------------------------------------------
with tab1:
    st.subheader("Ask about Saudi Labor Law" if language == "English" else "اسأل عن نظام العمل السعودي")

    use_employee_data = st.checkbox(
        "Include my employee data" if language == "English" else "استخدام بيانات الموظف في الإجابة"
    )

    user_input = st.text_area("Enter your question:" if language == "English" else "أدخل سؤالك هنا:")

    employee_data = None
    if use_employee_data:
        with st.expander("🧾 Enter Employee Information" if language == "English" else "🧾 أدخل بيانات الموظف"):
            name = st.text_input("Name" if language == "English" else "الاسم")
            job = st.text_input("Job Title" if language == "English" else "المسمى الوظيفي")
            age = st.number_input("Age" if language == "English" else "العمر", 18, 70, 30)
            service_years = st.number_input("Service Years" if language == "English" else "سنوات الخدمة", 0, 40, 5)
            annual_leave_days = st.number_input("Annual Leave Requested" if language == "English" else "رصيد الإجازة الحالي", 0, 60, 21)
            sick_leave_days = st.number_input("Sick Leave Requested" if language == "English" else "أيام الإجازة المرضية", 0, 60, 0)
            basic_wage = st.number_input("Basic Wage" if language == "English" else "الراتب الأساسي", 0, 100000, 5000)
            total_salary = st.number_input("Total Salary" if language == "English" else "إجمالي الراتب", 0, 100000, 7000)

            employee_data = {
                "name": name,
                "job": job,
                "age": age,
                "service_years": service_years,
                "annual_leave_days": annual_leave_days,
                "sick_leave_days": sick_leave_days,
                "basic_wage": basic_wage,
                "total_salary": total_salary,
            }

    if st.button("Ask" if language == "English" else "اسأل"):
        if not user_input.strip():
            st.warning("Please enter a question." if language == "English" else "يرجى إدخال السؤال.")
        else:
            with st.spinner("Searching legal articles..." if language == "English" else "جاري البحث في النظام..."):
                answer, refs = answer_policy_question(user_input, employee_data)

            st.markdown("### 🧠 Answer:" if language == "English" else "### 🧠 الإجابة:")
            st.markdown(answer)

            if refs:
                st.markdown("---")
                st.markdown("### 📖 Related Legal Articles:" if language == "English" else "### 📖 المواد القانونية ذات الصلة:")

                for r in refs:
                    st.markdown(
                        f"**{r['article_name']}** — 🔹 Similarity: `{r['similarity']}`"
                    )
                    with st.expander(
                        f"📘 {r['part']} → {r['chapter']} → {r['article_number']}"
                        if language == "English"
                        else f"📘 {r['part']} ← {r['chapter']} ← {r['article_number']}"
                    ):
                        st.write(r["arabic_content"])
                        if r["english_content"]:
                            st.markdown("**English Translation:**")
                            st.write(r["english_content"])
