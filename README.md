# Tamil Nadu Government Welfare Schemes - RAG Chatbot

An intelligent Retrieval-Augmented Generation (RAG) chatbot that helps citizens discover and understand Tamil Nadu Government agriculture and farmer welfare schemes ([tn.gov.in](https://www.tn.gov.in/scheme_list.php?dep_id=Mg==)).

## Architecture
- **Data Extraction**: Custom scraper (`scraper.py`) targeting the TN schemes portal.
- **Vector Store**: FAISS (Facebook AI Similarity Search) for local vector indexing.
- **Embeddings**: OpenAI `text-embedding-3-small`.
- **LLM Engine**: OpenAI `gpt-4o-mini` with strict factual grounding prompts.
- **User Interface**: Streamlit web application with chat history and source citations.

## Setup & Installation

1. Clone the repository and navigate into the directory:
   ```cmd
   git clone <your-repo-url>
   cd tn-schemes-rag-chatbot