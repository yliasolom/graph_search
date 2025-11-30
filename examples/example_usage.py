"""Example usage of all RAG and agent systems."""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag.vector_rag import VectorRAG
from src.graph.graph_rag import GraphRAG
from src.agents.news_analysis_agent import NewsAnalysisAgent


def example_vector_rag():
    """Example: Using Vector RAG for semantic search."""
    print("\n" + "="*60)
    print("EXAMPLE: Vector RAG")
    print("="*60)

    # Initialize Vector RAG
    rag = VectorRAG()

    # Build vector database from news
    print("\n1. Building vector database...")
    rag.fetch_and_build(
        queries=["artificial intelligence 2024", "machine learning"],
        page_size=3
    )

    # Query the system
    print("\n2. Querying Vector RAG...")
    questions = [
        "What are the latest developments in AI?",
        "What is machine learning being used for?"
    ]

    for question in questions:
        print(f"\nQ: {question}")
        answer = rag.query(question, k=3)
        print(f"A: {answer}\n")


def example_graph_rag():
    """Example: Using Graph RAG with Neo4j."""
    print("\n" + "="*60)
    print("EXAMPLE: Graph RAG")
    print("="*60)

    graph_rag = GraphRAG()

    try:
        # Build knowledge and lexical graphs
        print("\n1. Building graph database...")
        graph_rag.build_full_graph(start_clean=True)

        # Query the graph
        print("\n2. Querying Graph RAG...")
        questions = [
            "Which basketball and hockey teams share the same venue?",
            "What are the latest NBA news?",
            "Tell me about NHL teams in Canada."
        ]

        for question in questions:
            print(f"\nQ: {question}")
            answer = graph_rag.query(question)
            print(f"A: {answer}\n")

    finally:
        graph_rag.close()


def example_news_analysis_agent():
    """Example: Using Multi-Agent News Analysis."""
    print("\n" + "="*60)
    print("EXAMPLE: Multi-Agent News Analysis")
    print("="*60)

    # Initialize agent
    agent = NewsAnalysisAgent()

    # Run analysis on different topics
    topics = [
        "artificial intelligence",
        "climate change",
        "space exploration"
    ]

    for topic in topics:
        print(f"\n\nAnalyzing topic: {topic}")
        print("-" * 40)

        result = agent.run(topic)

        if result.get("error"):
            print(f"Error: {result['error']}")
            continue

        print(f"\nArticles found: {len(result.get('articles', []))}")
        print(f"Articles analyzed: {len(result.get('analysis_results', []))}")

        print("\nAnalysis Results:")
        for i, analysis in enumerate(result.get('analysis_results', []), 1):
            print(f"\n{i}. {analysis['article_title']}")
            print(f"   Topic: {analysis['topic']}")
            print(f"   Sentiment: {analysis['sentiment']}")
            print(f"   Importance: {analysis['importance']}/10")

        print("\n" + "="*60)
        print("FINAL SUMMARY")
        print("="*60)
        print(result.get('final_summary', 'No summary available'))


def example_combined_workflow():
    """Example: Combined workflow using multiple systems."""
    print("\n" + "="*60)
    print("EXAMPLE: Combined Workflow")
    print("="*60)

    # Step 1: Use agent to analyze news
    print("\n1. Analyzing news with Multi-Agent system...")
    agent = NewsAnalysisAgent()
    analysis_result = agent.run("technology trends 2024")

    # Step 2: Build vector RAG from the same topic
    print("\n2. Building Vector RAG on the same topic...")
    vector_rag = VectorRAG()
    vector_rag.fetch_and_build(["technology trends 2024"], page_size=5)

    # Step 3: Compare results
    print("\n3. Comparing results...")

    print("\nAgent Summary:")
    print(analysis_result.get('final_summary', 'N/A')[:300] + "...")

    print("\nVector RAG Answer:")
    answer = vector_rag.query("What are the main technology trends in 2024?")
    print(answer[:300] + "...")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("RAG & MULTI-AGENT SYSTEM EXAMPLES")
    print("="*60)

    examples = [
        ("Vector RAG", example_vector_rag),
        ("Graph RAG", example_graph_rag),
        ("Multi-Agent Analysis", example_news_analysis_agent),
        ("Combined Workflow", example_combined_workflow)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all examples")

    choice = input("\nSelect example to run (0-4): ").strip()

    if choice == "0":
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\nError in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            print(f"\nError: {e}")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
