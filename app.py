import streamlit as st
from rag_engine import query_schemes

# Page configuration
st.set_page_config(
    page_title="TN Government Schemes RAG Chatbot",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 Tamil Nadu Welfare Schemes Assistant")
st.caption("Powered by RAG (FAISS + OpenAI GPT-4o-mini) | Source: [tn.gov.in](https://www.tn.gov.in/scheme_list.php?dep_id=Mg==)")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Vanakkam! I am your Tamil Nadu Government Welfare Schemes assistant. How can I help you today? You can ask about subsidies, eligibility, or application steps for agriculture schemes."
        }
    ]

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Verified Source Schemes"):
                for doc in msg["sources"]:
                    st.markdown(f"- **{doc.metadata.get('title')}** ([Portal Link]({doc.metadata.get('url')}))")

# User input box
if user_prompt := st.chat_input("Ask a question (e.g., 'What is the Kuruvai Cultivation Package?')..."):
    # 1. Display user query
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Generate RAG answer
    with st.chat_message("assistant"):
        with st.spinner("Searching official portal records and generating answer..."):
            try:
                answer, sources = query_schemes(user_prompt)
                st.markdown(answer)

                if sources:
                    with st.expander("📚 Verified Source Schemes"):
                        for doc in sources:
                            st.markdown(f"- **{doc.metadata.get('title')}** ([Portal Link]({doc.metadata.get('url')}))")

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                error_msg = f"An error occurred while answering: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})