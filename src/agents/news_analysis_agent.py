"""Multi-agent system for news analysis using LangGraph."""
import json
import time
from typing import TypedDict, List, Dict, Any, Literal
from openai import OpenAI
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from src.core.config import init_settings
from src.core.logger import log
from src.core.utils import fetch_news, fetch_article_text


settings = init_settings()


class NewsAnalysisState(TypedDict):
    """State definition for news analysis workflow."""
    query: str
    articles: List[Dict[str, Any]]
    analysis_results: List[Dict[str, Any]]
    final_summary: str
    error: str
    step_count: int


class NewsAnalysisAgent:
    """Multi-agent system for news analysis."""

    def __init__(self):
        """Initialize agents with OpenAI clients."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model=settings.default_model,
            temperature=settings.default_temperature
        )
        self.graph = None

    def research_agent(self, state: NewsAnalysisState) -> NewsAnalysisState:
        """Agent for news collection."""
        log.info(f"Research Agent: searching news for query '{state['query']}'")

        try:
            # Optimize query for NewsAPI by extracting key terms
            # Convert natural language query to optimized search query
            query_optimization_prompt = f"""
Convert the following user query into an optimized search query for a news API.
Extract only the key terms and topics, remove question words and common words.
Return only the optimized search query, nothing else.

User query: "{state['query']}"

Optimized search query:"""

            try:
                optimization_response = self.client.chat.completions.create(
                    model=settings.default_model,
                    messages=[{"role": "user", "content": query_optimization_prompt}],
                    temperature=0.1,
                    max_tokens=50
                )
                optimized_query = optimization_response.choices[0].message.content.strip()
                # Remove quotes if LLM added them
                optimized_query = optimized_query.strip('"').strip("'")
                log.info(f"Optimized query: '{state['query']}' -> '{optimized_query}'")
            except Exception as e:
                log.warning(f"Query optimization failed, using original: {e}")
                optimized_query = state["query"]

            articles = fetch_news(optimized_query, page_size=3)

            if not articles:
                return {
                    **state,
                    "error": "No articles found",
                    "step_count": state["step_count"] + 1
                }

            # Fetch full article content
            for article in articles:
                if article.get("url"):
                    content = fetch_article_text(article["url"])
                    article["content"] = content or article.get("description", "")
                time.sleep(1)  # Delay to avoid rate limiting

            log.info(f"Found {len(articles)} articles")

            return {
                **state,
                "articles": articles,
                "step_count": state["step_count"] + 1
            }
        except Exception as e:
            log.error(f"Error in research agent: {e}")
            return {
                **state,
                "error": f"Error in research agent: {str(e)}",
                "step_count": state["step_count"] + 1
            }

    def analysis_agent(self, state: NewsAnalysisState) -> NewsAnalysisState:
        """Agent for news analysis."""
        log.info("Analysis Agent: analyzing collected news")

        if not state.get("articles"):
            return {
                **state,
                "error": "No articles to analyze",
                "step_count": state["step_count"] + 1
            }

        try:
            analysis_results = []

            for article in state["articles"]:
                content = article.get("content", article.get("description", ""))
                if not content:
                    continue

                prompt = f"""
Analyze the following news and determine:
1. Main topic (1-2 words)
2. Sentiment (positive/negative/neutral)
3. Key facts (3-5 points)
4. Importance (1-10)

Title: {article.get('title', '')}
Text: {content[:1000]}

Answer in JSON format:
{{
    "topic": "topic",
    "sentiment": "sentiment",
    "key_facts": ["fact1", "fact2", "fact3"],
    "importance": number
}}
"""

                response = self.client.chat.completions.create(
                    model=settings.default_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=settings.default_temperature
                )

                try:
                    analysis = json.loads(response.choices[0].message.content)
                    analysis["article_title"] = article.get("title", "")
                    analysis["source"] = article.get("source", {}).get("name", "")
                    analysis_results.append(analysis)
                except json.JSONDecodeError:
                    analysis_results.append({
                        "article_title": article.get("title", ""),
                        "topic": "Unknown",
                        "sentiment": "neutral",
                        "key_facts": ["Could not analyze"],
                        "importance": 5
                    })

            log.info(f"Analyzed {len(analysis_results)} articles")

            return {
                **state,
                "analysis_results": analysis_results,
                "step_count": state["step_count"] + 1
            }
        except Exception as e:
            log.error(f"Error in analysis agent: {e}")
            return {
                **state,
                "error": f"Error in analysis agent: {str(e)}",
                "step_count": state["step_count"] + 1
            }

    def summary_agent(self, state: NewsAnalysisState) -> NewsAnalysisState:
        """Agent for creating final report."""
        log.info("Summary Agent: creating final report")

        if not state.get("analysis_results"):
            return {
                **state,
                "error": "No analysis results to create summary",
                "step_count": state["step_count"] + 1
            }

        try:
            analysis_data = json.dumps(state["analysis_results"], ensure_ascii=False, indent=2)

            prompt = f"""
Based on news analysis for query "{state['query']}" create a brief final report.

Analysis data:
{analysis_data}

Report should contain:
1. Overall situation assessment
2. Main topics and trends
3. Key findings
4. Recommendations (if applicable)

Report should be in English, structured and informative.
"""

            response = self.client.chat.completions.create(
                model=settings.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            summary = response.choices[0].message.content
            log.info("Final report created")

            return {
                **state,
                "final_summary": summary,
                "step_count": state["step_count"] + 1
            }
        except Exception as e:
            log.error(f"Error in summary agent: {e}")
            return {
                **state,
                "error": f"Error in summary agent: {str(e)}",
                "step_count": state["step_count"] + 1
            }

    def should_continue(self, state: NewsAnalysisState) -> Literal["analysis", "summary", "end", "error_handler"]:
        """Determine next step in graph."""
        if state.get("error"):
            return "error_handler"

        if state["step_count"] == 1:
            return "analysis"
        elif state["step_count"] == 2:
            return "summary"
        else:
            return "end"

    def error_handler(self, state: NewsAnalysisState) -> NewsAnalysisState:
        """Handle errors in workflow."""
        error_msg = state.get('error', 'Unknown error')
        log.error(f"Workflow error: {error_msg}")
        return {
            **state,
            "final_summary": f"An error occurred: {error_msg}"
        }

    def create_graph(self) -> StateGraph:
        """Create the news analysis workflow graph."""
        workflow = StateGraph(NewsAnalysisState)

        # Add nodes
        workflow.add_node("research", self.research_agent)
        workflow.add_node("analysis", self.analysis_agent)
        workflow.add_node("summary", self.summary_agent)
        workflow.add_node("error_handler", self.error_handler)

        # Set entry point
        workflow.set_entry_point("research")

        # Add conditional edges
        workflow.add_conditional_edges(
            "research",
            self.should_continue,
            {
                "analysis": "analysis",
                "error_handler": "error_handler",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "analysis",
            self.should_continue,
            {
                "summary": "summary",
                "error_handler": "error_handler",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "summary",
            self.should_continue,
            {
                "end": END,
                "error_handler": "error_handler"
            }
        )

        workflow.add_edge("error_handler", END)

        self.graph = workflow.compile()
        return self.graph

    def run(self, query: str) -> Dict[str, Any]:
        """
        Run news analysis for a query.

        Args:
            query: Search query for news

        Returns:
            Analysis results dictionary
        """
        log.info(f"Starting news analysis for query: '{query}'")

        if self.graph is None:
            self.create_graph()

        initial_state = {
            "query": query,
            "articles": [],
            "analysis_results": [],
            "final_summary": "",
            "error": "",
            "step_count": 0
        }

        result = self.graph.invoke(initial_state)

        log.info("News analysis completed")

        return result


def demo():
    """Demo function for news analysis agent."""
    agent = NewsAnalysisAgent()
    result = agent.run("artificial intelligence")

    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)

    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print(f"Articles found: {len(result.get('articles', []))}")
        print(f"Analyzed: {len(result.get('analysis_results', []))}")
        print("\nFINAL REPORT:")
        print("-" * 40)
        print(result.get("final_summary", "Report not created"))


if __name__ == "__main__":
    demo()
