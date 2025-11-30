#!/usr/bin/env python3
"""
Simple script to run Multi-Agent news analysis system.
"""
import sys
from src.agents.news_analysis_agent import NewsAnalysisAgent


def main():
    """Run Multi-Agent analysis."""
    print("\n" + "=" * 60)
    print("MULTI-AGENT NEWS ANALYSIS SYSTEM")
    print("=" * 60)
    
    # Get query from user
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("\nEnter topic for news analysis (e.g., 'artificial intelligence'): ").strip()
        if not query:
            query = "artificial intelligence"
            print(f"Using default topic: {query}")
    
    print(f"\n🔍 Analyzing news on topic: '{query}'")
    print("-" * 60)
    
    try:
        # Create agent
        agent = NewsAnalysisAgent()
        
        # Run analysis
        result = agent.run(query)
        
        # Display results
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        if result.get("error"):
            print(f"\n❌ Error: {result['error']}")
            return
        
        print(f"\n📰 Articles found: {len(result.get('articles', []))}")
        print(f"✅ Analyzed: {len(result.get('analysis_results', []))}")
        
        # Show analysis for each article
        if result.get('analysis_results'):
            print("\n" + "-" * 60)
            print("ARTICLE ANALYSIS:")
            print("-" * 60)
            
            for i, analysis in enumerate(result.get('analysis_results', []), 1):
                print(f"\n{i}. {analysis.get('article_title', 'Untitled')}")
                print(f"   📌 Topic: {analysis.get('topic', 'N/A')}")
                print(f"   😊 Sentiment: {analysis.get('sentiment', 'N/A')}")
                print(f"   ⭐ Importance: {analysis.get('importance', 'N/A')}/10")
                print(f"   📍 Source: {analysis.get('source', 'N/A')}")
                
                key_facts = analysis.get('key_facts', [])
                if key_facts:
                    print(f"   🔑 Key Facts:")
                    for fact in key_facts[:3]:  # Show first 3
                        print(f"      • {fact}")
        
        # Show final report
        if result.get('final_summary'):
            print("\n" + "=" * 60)
            print("FINAL REPORT")
            print("=" * 60)
            print(result.get('final_summary'))
        
        print("\n" + "=" * 60)
        print("✅ Analysis completed!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("\nMake sure that:")
        print("1. All dependencies are installed: pip install -r requirements.txt")
        print("2. .env file is configured with OPENAI_API_KEY and NEWS_API_KEY")
        sys.exit(1)


if __name__ == "__main__":
    main()

