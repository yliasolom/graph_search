"""Basic RAG implementation using FAISS vector store."""
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from src.core.config import init_settings
from src.core.logger import log
from src.core.utils import fetch_news, fetch_article


settings = init_settings()


class VectorRAG:
    """RAG system using vector embeddings and FAISS."""

    def __init__(self):
        """Initialize VectorRAG with OpenAI client and embeddings."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.vector_db = None

    def build_vector_db(self, articles: List[Dict[str, Any]]) -> FAISS:
        """
        Build FAISS vector store from articles.

        Args:
            articles: List of article dictionaries with text content

        Returns:
            FAISS vector store instance
        """
        log.info(f"Building vector database from {len(articles)} articles")

        texts = [a["text"] for a in articles if a.get("text")]
        metadatas = [{"title": a["title"], "url": a["url"]} for a in articles if a.get("text")]

        # Split into chunks for better retrieval
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

        docs = []
        for text, meta in zip(texts, metadatas):
            for chunk in splitter.split_text(text):
                docs.append(Document(page_content=chunk, metadata=meta))

        log.info(f"Created {len(docs)} document chunks")

        self.vector_db = FAISS.from_documents(docs, self.embeddings)
        return self.vector_db

    def query(self, question: str, k: int = None) -> Tuple[str, List[Document], str]:
        """
        Query the RAG system with a question.

        Args:
            question: User question
            k: Number of documents to retrieve (default from settings)

        Returns:
            Tuple containing generated answer, retrieved documents, and raw context string
        """
        if k is None:
            k = settings.top_k_results

        if self.vector_db is None:
            raise ValueError("Vector database not initialized. Call build_vector_db first.")

        log.info(f"Querying: {question}")

        # Retrieve relevant documents
        results = self.vector_db.similarity_search(question, k=k)
        context = "\n\n".join([r.page_content for r in results])

        # Generate answer using LLM
        prompt = f"""You are a helpful assistant.
Answer the question *only* using the context below.
If the context does not provide an answer, say you don't know.

Context:
{context}

Question: {question}
Answer:"""

        response = self.client.chat.completions.create(
            model=settings.default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.default_temperature,
            max_tokens=settings.max_tokens
        )

        answer = response.choices[0].message.content
        log.info(f"Generated answer: {answer[:100]}...")

        return answer, results, context

    def fetch_and_build(self, queries: List[str], page_size: int = 3) -> None:
        """
        Fetch news articles and build vector database.

        Args:
            queries: List of search queries
            page_size: Number of articles per query
        """
        articles = []
        for query in queries:
            log.info(f"Fetching news for: {query}")
            news = fetch_news(query, page_size=page_size)
            for n in news:
                article = fetch_article(n)
                if article:
                    articles.append(article)
                else:
                    log.debug(f"No usable text for article from query '{query}'")

        log.info(f"Fetched total {len(articles)} articles")
        self.build_vector_db(articles)


def demo():
    """Demo function for basic RAG."""
    rag = VectorRAG()

    # Fetch and build vector DB
    rag.fetch_and_build(["NBA 2024-2025", "NHL 2024-2025"], page_size=3)

    # Query
    question = "Which basketball and ice hockey teams share the same venue?"
    answer, documents, _ = rag.query(question)

    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")
    print(f"Sources: {[doc.metadata for doc in documents]}")


if __name__ == "__main__":
    demo()
