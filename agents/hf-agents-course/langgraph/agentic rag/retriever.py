#We will use the BM25Retriever from the langchain_community.retrievers module to create a retriever tool.

#The BM25Retriever is a great starting point for retrieval, but for more advanced semantic search, you might consider using embedding-based retrievers like those from sentence-transformers.

from langchain_community.retrievers import BM25Retriever
from langchain_core.tools import Tool
from data import docs

bm25_retriever = BM25Retriever.from_documents(docs)

def extract_text(query: str) -> str:
    """Retrieves detailed information about gala guests based on their name or relation."""
    results = bm25_retriever.invoke(query)
    if results:
        return "\n\n".join([doc.page_content for doc in results[:3]])
    else:
        return "No matching guest information found."

guest_info_tool = Tool(
    name="guest_info_retriever",
    func=extract_text,
    description="Retrieves detailed information about gala guests based on their name or relation."
)