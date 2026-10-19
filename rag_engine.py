import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

INDEX_DIR = os.path.join("data", "faiss_index")

# Prompt template enforcing strict grounding in official portal records
PROMPT_TEMPLATE = """You are an official Tamil Nadu Government Schemes Assistant.
Answer the citizen's question based strictly on the official scheme context provided below.
If the answer is not contained in the context, clearly say: "I do not have verified records from the official portal for that question."
Do not fabricate eligibility criteria or monetary amounts. Always cite the Scheme Name, Department, and application procedure.

Official Context:
{context}

User Question: {question}

Helpful & Grounded Answer:"""

def format_docs(docs):
    """Format retrieved documents for the LLM prompt."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    """Load FAISS index and assemble the LangChain RAG pipeline."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY missing from .env file!")

    # 1. Load the same OpenAI embeddings model used to build the index
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=openai_key
    )

    # 2. Load FAISS index from disk
    vectorstore = FAISS.load_local(
        INDEX_DIR, 
        embeddings, 
        allow_dangerous_deserialization=True
    )

    # 3. Retrieve top 2 most relevant scheme documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    # 4. Initialize GPT-4o-mini with low temperature for factual precision
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=openai_key
    )

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

    # 5. Assemble LCEL chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever

def query_schemes(user_question: str):
    """Helper to query the pipeline and return the answer + source documents."""
    chain, retriever = get_rag_chain()
    source_docs = retriever.invoke(user_question)
    answer = chain.invoke(user_question)
    return answer, source_docs

if __name__ == "__main__":
    test_question = "What subsidy is available for solar powered pump sets?"
    print(f"\nQuerying: '{test_question}'\n" + "=" * 50)

    answer, sources = query_schemes(test_question)
    print("\n--- Answer ---")
    print(answer)
    print("\n--- Retrieved Source Documents ---")
    for i, doc in enumerate(sources, start=1):
        print(f"[{i}] {doc.metadata.get('title')} ({doc.metadata.get('url')})")