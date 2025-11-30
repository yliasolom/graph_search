"""
Streamlit Web Interface for RAG & Multi-Agent Analysis System

Beautiful web interface for working with:
- Vector RAG: semantic search through FAISS
- Graph RAG: Neo4j graph database
- Multi-Agent System: news analysis through LangGraph
"""
import streamlit as st
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag.vector_rag import VectorRAG
from src.graph.graph_rag import GraphRAG
from src.agents.news_analysis_agent import NewsAnalysisAgent
from src.core.logger import log


# Page configuration
st.set_page_config(
    page_title="RAG & Multi-Agent Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styles
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background: #f0f2f6;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'vector_rag' not in st.session_state:
    st.session_state.vector_rag = None
if 'graph_rag' not in st.session_state:
    st.session_state.graph_rag = None
if 'vector_db_built' not in st.session_state:
    st.session_state.vector_db_built = False
if 'graph_db_built' not in st.session_state:
    st.session_state.graph_db_built = False


def show_header():
    """Displays the application header."""
    st.markdown('<h1 class="main-header">🔍 RAG & Multi-Agent Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Semantic search, graph analysis, and multi-agent news processing system</p>', unsafe_allow_html=True)
    st.markdown("---")


def vector_rag_page():
    """Page for working with Vector RAG."""
    st.header("📚 Vector RAG - Semantic Search")
    st.markdown("Vector similarity search system using FAISS and OpenAI embeddings")
    
    tab1, tab2 = st.tabs(["🔨 Build Database", "❓ Queries"])
    
    with tab1:
        st.subheader("Build Vector Database")
        st.markdown("Load news articles and create a vector store for semantic search")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            queries_input = st.text_area(
                "Search queries for news",
                placeholder="Enter queries separated by commas or one per line\nExample: artificial intelligence, machine learning, neural networks",
                height=100
            )
        
        with col2:
            page_size = st.number_input(
                "Articles per query",
                min_value=1,
                max_value=20,
                value=3,
                help="Number of articles for each query"
            )
        
        if st.button("🔨 Build Vector Database", type="primary", use_container_width=True):
            if not queries_input.strip():
                st.error("⚠️ Please enter at least one query")
            else:
                # Parse queries
                queries = [q.strip() for q in queries_input.replace(",", "\n").split("\n") if q.strip()]
                
                with st.spinner(f"🔨 Building vector database from {len(queries)} queries..."):
                    try:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("Initializing Vector RAG...")
                        vector_rag = VectorRAG()
                        progress_bar.progress(20)
                        
                        status_text.text(f"Loading news for {len(queries)} queries...")
                        vector_rag.fetch_and_build(queries=queries, page_size=page_size)
                        progress_bar.progress(80)
                        
                        st.session_state.vector_rag = vector_rag
                        st.session_state.vector_db_built = True
                        progress_bar.progress(100)
                        
                        st.success(f"✅ Vector database built successfully! Processed {len(queries)} queries")
                        
                        # Show statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Queries processed", len(queries))
                        with col2:
                            st.metric("Articles per query", page_size)
                        with col3:
                            st.metric("Total articles", len(queries) * page_size)
                        
                    except Exception as e:
                        st.error(f"❌ Error building database: {str(e)}")
                        log.error(f"Vector RAG build error: {e}")
        
        # Database status
        if st.session_state.vector_db_built:
            st.info("✅ Vector database built and ready to use")
        else:
            st.warning("⚠️ Vector database not built yet. Build the database before making queries.")
    
    with tab2:
        st.subheader("Query Vector RAG")
        
        if not st.session_state.vector_db_built:
            st.warning("⚠️ Please build the vector database first in the 'Build Database' tab")
        else:
            question = st.text_input(
                "Your question",
                placeholder="Example: What are the latest news about artificial intelligence?",
                key="vector_question"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                k = st.number_input("Number of documents", min_value=1, max_value=10, value=3)
            
            if st.button("🔍 Find Answer", type="primary", use_container_width=True):
                if not question.strip():
                    st.error("⚠️ Please enter a question")
                else:
                    with st.spinner("🔍 Searching for answer..."):
                        try:
                            answer, documents, context = st.session_state.vector_rag.query(question, k=k)
                            
                            # Display answer
                            st.markdown("### 💡 Answer")
                            st.markdown(f'<div class="success-box">{answer}</div>', unsafe_allow_html=True)
                            
                            # Display found documents
                            if documents:
                                st.markdown("### 📄 Retrieved Documents")
                                for i, doc in enumerate(documents, 1):
                                    with st.expander(f"📄 Document {i}: {doc.metadata.get('title', 'Untitled')}", expanded=False):
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            st.markdown(f"**URL:** {doc.metadata.get('url', 'Not specified')}")
                                        with col2:
                                            st.markdown(f"**Size:** {len(doc.page_content)} characters")
                                        st.markdown("**Content:**")
                                        st.text_area(
                                            "",
                                            doc.page_content,
                                            height=150,
                                            disabled=True,
                                            key=f"doc_{i}"
                                        )
                            
                            # Context (optional)
                            with st.expander("🔍 Show Full Context", expanded=False):
                                st.text_area("Context used for answer generation", context, height=300, disabled=True)
                        
                        except Exception as e:
                            st.error(f"❌ Error querying: {str(e)}")
                            log.error(f"Vector RAG query error: {e}")


def graph_rag_page():
    """Page for working with Graph RAG."""
    st.header("🕸️ Graph RAG - Graph Database")
    st.markdown("Work with Neo4j graph database for structured search")
    
    tab1, tab2 = st.tabs(["🔨 Build Graph", "❓ Queries"])
    
    with tab1:
        st.subheader("Build Graph Database")
        st.markdown("Create knowledge graph and lexical graph from news")
        
        # Build options
        start_clean = st.checkbox("Clear existing graph before building", value=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Knowledge Graph")
            leagues_input = st.text_area(
                "Leagues/Topics for knowledge graph",
                placeholder="Example: NBA, NHL, Premier League\n(leave empty if not needed)",
                height=100,
                help="List of leagues or topics for building knowledge graph"
            )
        
        with col2:
            st.markdown("#### Lexical Graph")
            news_queries_input = st.text_area(
                "Queries for lexical graph",
                placeholder="Example: NBA news, hockey updates\n(leave empty if not needed)",
                height=100,
                help="Queries for building lexical graph from news"
            )
            page_size = st.number_input(
                "Articles per query",
                min_value=1,
                max_value=20,
                value=10,
                key="graph_page_size"
            )
        
        if st.button("🔨 Build Graph Database", type="primary", use_container_width=True):
            if not leagues_input.strip() and not news_queries_input.strip():
                st.error("⚠️ Please specify at least one graph type to build")
            else:
                leagues = [l.strip() for l in leagues_input.split("\n") if l.strip()] if leagues_input.strip() else None
                news_queries = [q.strip() for q in news_queries_input.split("\n") if q.strip()] if news_queries_input.strip() else None
                
                with st.spinner("🔨 Building graph database..."):
                    try:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("Initializing Graph RAG...")
                        if st.session_state.graph_rag is None:
                            graph_rag = GraphRAG()
                        else:
                            graph_rag = st.session_state.graph_rag
                        progress_bar.progress(20)
                        
                        if start_clean:
                            status_text.text("Clearing existing graph...")
                            graph_rag.erase_graph()
                            progress_bar.progress(30)
                        
                        if leagues:
                            status_text.text(f"Building knowledge graph for {len(leagues)} leagues...")
                            graph_rag.build_knowledge_graph(leagues=leagues)
                            progress_bar.progress(60)
                        
                        if news_queries:
                            status_text.text(f"Building lexical graph for {len(news_queries)} queries...")
                            graph_rag.build_lexical_graph(queries=news_queries, page_size=page_size)
                            progress_bar.progress(90)
                        
                        st.session_state.graph_rag = graph_rag
                        st.session_state.graph_db_built = True
                        progress_bar.progress(100)
                        
                        st.success("✅ Graph database built successfully!")
                        
                        # Statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Knowledge Graph", "✅" if leagues else "❌")
                        with col2:
                            st.metric("Lexical Graph", "✅" if news_queries else "❌")
                        with col3:
                            st.metric("Status", "Ready")
                    
                    except Exception as e:
                        st.error(f"❌ Error building graph: {str(e)}")
                        log.error(f"Graph RAG build error: {e}")
        
        # Database status
        if st.session_state.graph_db_built:
            st.info("✅ Graph database built and ready to use")
        else:
            st.warning("⚠️ Graph database not built yet. Build the database before making queries.")
    
    with tab2:
        st.subheader("Query Graph RAG")
        
        if not st.session_state.graph_db_built:
            st.warning("⚠️ Please build the graph database first in the 'Build Graph' tab")
        else:
            question = st.text_input(
                "Your question",
                placeholder="Example: Which basketball and hockey teams use the same stadium?",
                key="graph_question"
            )
            
            if st.button("🔍 Find Answer", type="primary", use_container_width=True):
                if not question.strip():
                    st.error("⚠️ Please enter a question")
                else:
                    with st.spinner("🔍 Searching for answer in graph..."):
                        try:
                            answer = st.session_state.graph_rag.query(question)
                            
                            # Display answer
                            st.markdown("### 💡 Answer")
                            st.markdown(f'<div class="success-box">{answer}</div>', unsafe_allow_html=True)
                        
                        except Exception as e:
                            st.error(f"❌ Error querying: {str(e)}")
                            log.error(f"Graph RAG query error: {e}")


def news_analysis_page():
    """Page for multi-agent news analysis."""
    st.header("🤖 Multi-Agent News Analysis")
    st.markdown("News analysis using multi-agent system based on LangGraph")
    
    query = st.text_input(
        "Topic for analysis",
        placeholder="Example: artificial intelligence, climate change, space exploration",
        key="news_query"
    )
    
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        if not query.strip():
            st.error("⚠️ Please enter a topic for analysis")
        else:
            with st.spinner("🤖 Running multi-agent news analysis..."):
                try:
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Initializing agents...")
                    agent = NewsAnalysisAgent()
                    progress_bar.progress(10)
                    
                    status_text.text("Searching for news...")
                    result = agent.run(query)
                    progress_bar.progress(50)
                    
                    if result.get("error"):
                        st.error(f"❌ Error: {result['error']}")
                        return
                    
                    status_text.text("Processing results...")
                    progress_bar.progress(90)
                    
                    # Results header
                    st.markdown("---")
                    st.markdown("### 📊 Analysis Results")
                    
                    # Metrics
                    articles = result.get("articles", [])
                    analysis_results = result.get("analysis_results", [])
                    articles_found = len(articles)
                    articles_analyzed = len(analysis_results)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Articles Found", articles_found)
                    with col2:
                        st.metric("Analyzed", articles_analyzed)
                    with col3:
                        if analysis_results:
                            avg_importance = sum(a.get("importance", 0) for a in analysis_results) / len(analysis_results)
                            st.metric("Average Importance", f"{avg_importance:.1f}/10")
                        else:
                            st.metric("Average Importance", "N/A")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis completed!")
                    
                    # Article analysis
                    st.markdown("### 📰 Article Analysis")
                    
                    if not analysis_results:
                        if articles_found > 0:
                            st.warning(f"⚠️ Found {articles_found} articles, but analysis was not performed. Articles may not contain text or an error occurred during analysis.")
                        else:
                            st.warning("⚠️ No articles found. Check the query or News API availability.")
                        
                        # Show debug information
                        with st.expander("🔍 Debug Information", expanded=False):
                            st.json({
                                "query": result.get("query", ""),
                                "articles_count": articles_found,
                                "analysis_results_count": articles_analyzed,
                                "error": result.get("error", "No errors"),
                                "has_articles": bool(articles),
                                "has_final_summary": bool(result.get("final_summary")),
                                "step_count": result.get("step_count", 0)
                            })
                            
                            if articles_found > 0:
                                st.markdown("**Found articles:**")
                                for i, article in enumerate(articles[:3], 1):  # Show first 3
                                    st.markdown(f"{i}. {article.get('title', 'Untitled')}")
                                    st.caption(f"Source: {article.get('source', {}).get('name', 'Not specified')}")
                    
                    if analysis_results:
                        for i, analysis in enumerate(analysis_results, 1):
                            with st.expander(
                                f"📄 {i}. {analysis.get('article_title', 'Untitled')} | "
                                f"Topic: {analysis.get('topic', 'N/A')} | "
                                f"Sentiment: {analysis.get('sentiment', 'N/A')} | "
                                f"Importance: {analysis.get('importance', 0)}/10",
                                expanded=i == 1
                            ):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**Source:** {analysis.get('source', 'Not specified')}")
                                
                                with col2:
                                    sentiment = analysis.get('sentiment', 'neutral').lower()
                                    if sentiment == 'positive':
                                        sentiment_emoji = "✅"
                                        sentiment_color = "green"
                                    elif sentiment == 'negative':
                                        sentiment_emoji = "❌"
                                        sentiment_color = "red"
                                    else:
                                        sentiment_emoji = "➖"
                                        sentiment_color = "gray"
                                    
                                    st.markdown(f"**Sentiment:** {sentiment_emoji} {analysis.get('sentiment', 'neutral')}")
                                
                                st.markdown("**Key Facts:**")
                                key_facts = analysis.get('key_facts', [])
                                for fact in key_facts:
                                    st.markdown(f"- {fact}")
                                
                                # Importance progress bar
                                importance = analysis.get('importance', 0)
                                st.progress(importance / 10)
                                st.caption(f"Importance: {importance}/10")
                    
                    # Final summary
                    if result.get("final_summary"):
                        st.markdown("---")
                        st.markdown("### 📝 Final Summary")
                        st.markdown(f'<div class="success-box">{result.get("final_summary")}</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    log.error(f"News analysis error: {e}")


def dashboard_page():
    """Page with general information and statistics."""
    st.header("📊 Dashboard")
    st.markdown("General system information and component status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Vector RAG",
            "✅ Ready" if st.session_state.vector_db_built else "❌ Not Built",
            delta=None
        )
    
    with col2:
        st.metric(
            "Graph RAG",
            "✅ Ready" if st.session_state.graph_db_built else "❌ Not Built",
            delta=None
        )
    
    with col3:
        st.metric("Multi-Agent", "✅ Available", delta=None)
    
    with col4:
        st.metric("API Status", "✅ Active", delta=None)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Quick Start")
    
    st.markdown("""
    #### 1. Vector RAG
    - Go to the **Vector RAG** tab
    - Enter queries to search for news
    - Build the vector database
    - Perform semantic queries
    
    #### 2. Graph RAG
    - Go to the **Graph RAG** tab
    - Configure knowledge graph and/or lexical graph
    - Build the graph database
    - Perform structured queries
    
    #### 3. Multi-Agent Analysis
    - Go to the **News Analysis** tab
    - Enter a topic for analysis
    - Get detailed analysis with sentiment and importance
    """)
    
    st.markdown("---")
    
    st.markdown("### 📚 About the System")
    
    st.markdown("""
    This system combines three powerful technologies:
    
    - **Vector RAG**: Semantic search based on vector representations using FAISS
    - **Graph RAG**: Structured search through Neo4j graph database
    - **Multi-Agent System**: Intelligent news analysis using LangGraph and multiple agents
    
    The system is built on:
    - OpenAI GPT for answer generation
    - LangChain for document processing
    - Neo4j for graph data
    - FAISS for vector search
    """)


def main():
    """Main application function."""
    show_header()
    
    # Sidebar menu
    with st.sidebar:
        st.markdown("## 🔍 RAG & Multi-Agent")
        st.markdown("### Analysis System")
        st.markdown("---")
        
        st.markdown("## 🧭 Navigation")
        page = st.radio(
            "Select section",
            ["📊 Dashboard", "📚 Vector RAG", "🕸️ Graph RAG", "🤖 News Analysis"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Component Status")
        
        vector_status = "✅ Built" if st.session_state.vector_db_built else "❌ Not Built"
        graph_status = "✅ Built" if st.session_state.graph_db_built else "❌ Not Built"
        
        st.markdown(f"- Vector RAG: {vector_status}")
        st.markdown(f"- Graph RAG: {graph_status}")
        st.markdown("- Multi-Agent: ✅ Available")
        
        st.markdown("---")
        
        if st.button("🔄 Reset State", use_container_width=True):
            # Close connections before reset
            if st.session_state.graph_rag is not None:
                try:
                    st.session_state.graph_rag.close()
                except Exception as e:
                    log.warning(f"Error closing GraphRAG: {e}")
            
            st.session_state.vector_rag = None
            st.session_state.graph_rag = None
            st.session_state.vector_db_built = False
            st.session_state.graph_db_built = False
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📖 Information")
        st.markdown("""
        **Version:** 1.0.0
        
        **Technologies:**
        - OpenAI GPT
        - LangChain
        - Neo4j
        - FAISS
        - Streamlit
        """)
    
    # Display selected page
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "📚 Vector RAG":
        vector_rag_page()
    elif page == "🕸️ Graph RAG":
        graph_rag_page()
    elif page == "🤖 News Analysis":
        news_analysis_page()


if __name__ == "__main__":
    main()

