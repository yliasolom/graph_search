"""Graph RAG implementation using Neo4j knowledge graph."""
from typing import List, Dict, Any
from neo4j import GraphDatabase
from openai import OpenAI

from src.core.config import init_settings
from src.core.logger import log
from src.core.utils import fetch_news, fetch_article, fetch_teams


settings = init_settings()


class GraphRAG:
    """RAG system using Neo4j graph database."""

    def __init__(self):
        """Initialize GraphRAG with Neo4j driver and OpenAI client."""
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.database = settings.neo4j_database

    def close(self):
        """Close Neo4j driver connection."""
        self.driver.close()

    def erase_graph(self):
        """Clear all data from the graph database."""
        log.warning("Erasing entire graph database")
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")

    def _insert_teams(self, tx, teams: List[Dict[str, Any]]):
        """Insert teams into knowledge graph."""
        for t in teams:
            tx.run("""
                MERGE (team:Team {
                    id: $id,
                    name: $name,
                    venue: $stadium,
                    location: $location
                })
                """,
                id=t.get("idTeam"),
                name=t.get("strTeam"),
                location=t.get("strLocation"),
                stadium=t.get("strStadium")
            )

    def build_knowledge_graph(self, leagues: List[str] = None):
        """
        Build knowledge graph from sports team data.

        Args:
            leagues: List of league names (default: ["NBA", "NHL"])
        """
        if leagues is None:
            leagues = ["NBA", "NHL"]

        log.info(f"Building knowledge graph for leagues: {leagues}")

        teams = []
        for league in leagues:
            league_teams = fetch_teams(league)
            teams.extend(league_teams)

        with self.driver.session(database=self.database) as session:
            session.execute_write(self._insert_teams, teams)

        log.info(f"Inserted {len(teams)} teams into knowledge graph")

    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        Extract keywords from text using OpenAI.

        Args:
            text: Input text
            top_k: Number of keywords to extract

        Returns:
            List of extracted keywords
        """
        prompt = f"Extract {top_k} important keywords from this text:\n\n{text}"
        resp = self.client.chat.completions.create(
            model=settings.default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        keywords = resp.choices[0].message.content.split(",")
        return [kw.strip().lower() for kw in keywords]

    def _insert_news(self, tx, articles: List[Dict[str, Any]]):
        """Insert news articles and keywords into lexical graph."""
        for article in articles:
            title = article.get("title", "")
            url = article.get("url", "")
            text = article.get("text", "")

            # Insert news node
            tx.run("""
                MERGE (n:News {title: $title, url: $url})
                SET n.text = $text
                """,
                title=title,
                url=url,
                text=text
            )

            # Insert keyword nodes and edges
            keywords = self.extract_keywords(text, top_k=5)
            for kw in keywords:
                tx.run("""
                    MERGE (k:Keyword {name: $kw})
                    WITH k
                    MATCH (n:News {title: $title})
                    MERGE (n)-[:MENTIONS]->(k)
                    """,
                    kw=kw,
                    title=title
                )

    def build_lexical_graph(self, queries: List[str] = None, page_size: int = 10):
        """
        Build lexical graph from news articles.

        Args:
            queries: List of search queries (default: NBA and NHL 2024-2025)
            page_size: Number of articles per query
        """
        if queries is None:
            queries = ["NBA 2024-2025", "NHL 2024-2025"]

        log.info(f"Building lexical graph for queries: {queries}")

        all_articles = []
        for query in queries:
            news = fetch_news(query, page_size=page_size)
            articles = []
            for n in news:
                article = fetch_article(n)
                if article:
                    articles.append(article)
                else:
                    log.debug(f"Skipping empty article for query '{query}'")
            all_articles.extend(articles)

        with self.driver.session(database=self.database) as session:
            session.execute_write(self._insert_news, all_articles)

        log.info(f"Inserted {len(all_articles)} news articles into lexical graph")

    def query(self, question: str, news_limit: int = 5) -> str:
        """
        Query the graph RAG system.

        Args:
            question: User question
            news_limit: Number of news articles to retrieve

        Returns:
            Generated answer based on graph context
        """
        log.info(f"Querying graph RAG: {question}")

        with self.driver.session(database=self.database) as session:
            # Retrieve news + keywords
            news_records = session.run("""
                MATCH (n:News)-[:MENTIONS]->(k:Keyword)
                RETURN n.title AS title, n.text AS text, collect(k.name) AS keywords
                LIMIT $limit
                """, limit=news_limit).data()

            # Retrieve teams + venues
            team_records = session.run("""
                MATCH (t1:Team), (t2:Team)
                WHERE t1.venue = t2.venue AND t1 <> t2
                RETURN t1.name AS team1, t2.name AS team2, t1.venue AS venue
                """).data()

        # Build context
        context_parts = []

        for r in news_records:
            snippet = r['text'][:300] + "..." if r.get('text') else ""
            context_parts.append(
                f"Title: {r['title']}\nKeywords: {', '.join(r['keywords'])}\nText: {snippet}"
            )

        for r in team_records:
            context_parts.append(
                f"Team1: {r['team1']}, Team2: {r['team2']}, Venue: {r['venue']}"
            )

        context = "\n\n".join(context_parts)

        # Query LLM
        prompt = f"""You can only use the following retrieved context to answer.

Context:
{context}

Question: {question}
Answer:"""

        resp = self.client.chat.completions.create(
            model=settings.default_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.default_temperature
        )

        answer = resp.choices[0].message.content
        log.info(f"Generated answer: {answer[:100]}...")

        return answer

    def build_full_graph(self, start_clean: bool = False):
        """
        Build both knowledge and lexical graphs.

        Args:
            start_clean: Whether to erase existing graph first
        """
        if start_clean:
            self.erase_graph()

        self.build_knowledge_graph()
        self.build_lexical_graph()


def demo():
    """Demo function for Graph RAG."""
    graph_rag = GraphRAG()

    try:
        # Build graphs
        graph_rag.build_full_graph(start_clean=True)

        # Query
        question = "Which basketball and ice hockey teams share the same venue?"
        answer = graph_rag.query(question)

        print(f"\nQuestion: {question}")
        print(f"Answer: {answer}")

    finally:
        graph_rag.close()


if __name__ == "__main__":
    demo()
