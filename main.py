import os
import streamlit as st
import asyncio
import nest_asyncio
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.output_parsers import StrOutputParser
from telegram import Bot
from langgraph.graph import StateGraph
from langgraph.constants import END
from typing import Dict, List
from langchain.schema import Document
from textwrap import shorten
from urllib.parse import urlparse

# Apply nest_asyncio to allow async code in Streamlit
nest_asyncio.apply()

# Load environment variables
os.environ["TELEGRAM_BOT_TOKEN"] = "YOUR_TELEGRAM_BOT_TOKEN"
os.environ["TELEGRAM_CHANNEL_ID"] = "YOUR_TELEGRAM_CHANNEL_ID"
os.environ["SERPER_API_KEY"] = "YOUR_SERPER_API_KEY"

# Initialize LLM
llm = OllamaLLM(model="qwen2.5:latest", temperature=0, num_gpu=1)

# Define prompt for keyword suggestion
keyword_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
    Given the user query: '{query}', suggest up to 3 search keywords 
    that would help find relevant articles on both Wikipedia and Medium.
    Return them as a comma-separated list.
    
    Example:
    Query: "machine learning"
    Keywords: "machine learning, artificial intelligence, deep learning"
    """
)

# Define prompt for article summarization
summary_prompt = PromptTemplate(
    input_variables=["text", "source"],
    template="""
    Create a concise summary of the following content from {source}. Follow these rules:
    1. Keep it under 350 characters (for Telegram)
    2. Start with a clear definition/overview
    3. Include key points
    4. Use bullet points for clarity
    5. Maintain appropriate tone for the source
    
    Article content:
    {text}
    
    Summary:
    """
)

# Define state for LangGraph
class State(Dict):
    query: str
    keywords: str
    wikipedia_urls: List[str]
    medium_urls: List[str]
    documents: List[Document]
    summary: str

def is_wikipedia_url(url: str) -> bool:
    """Check if URL is from Wikipedia"""
    parsed = urlparse(url)
    return parsed.netloc.endswith('wikipedia.org')

def is_medium_url(url: str) -> bool:
    """Check if URL is from Medium"""
    parsed = urlparse(url)
    return parsed.netloc.endswith('medium.com')

def suggest_keywords(state: State) -> State:
    query = state['query']
    keywords_chain = keyword_prompt | llm | StrOutputParser()
    keywords = keywords_chain.invoke({"query": query})
    print(keywords)
    state['keywords'] = keywords
    return state

def search_articles(state: State) -> State:
    search = GoogleSerperAPIWrapper()
    keywords = state['keywords'].split(", ")
    print(keywords)
    wikipedia_urls = []
    medium_urls = []
    
    for keyword in keywords:
        results = search.results(keyword.strip())
        
        if "organic" in results:
            for item in results["organic"]:
                if "link" in item:
                    url = item["link"]
                    if is_wikipedia_url(url):
                        wikipedia_urls.append(url)
                    elif is_medium_url(url):
                        medium_urls.append(url)
    
    # Remove duplicates and limit to 3 most relevant articles per source
    state['wikipedia_urls'] = list(set(wikipedia_urls))[:3]
    state['medium_urls'] = list(set(medium_urls))[:3]
    return state

def load_articles(state: State) -> State:
    all_urls = state.get('wikipedia_urls', []) + state.get('medium_urls', [])
    documents = []
    
    for url in all_urls:
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            
            # Add metadata about the source
            for doc in docs:
                if is_wikipedia_url(url):
                    doc.metadata["source"] = "Wikipedia"
                    parsed = urlparse(url)
                    doc.metadata["title"] = parsed.path.split("/")[-1].replace("_", " ")
                elif is_medium_url(url):
                    doc.metadata["source"] = "Medium"
                    doc.metadata["title"] = url.split("/")[-1].replace("-", " ")
            
            documents.extend(docs)
        except Exception as e:
            print(f"Failed to load article {url}: {e}")
    
    state['documents'] = documents
    return state

def summarize_articles(state: State) -> State:
    documents = state.get('documents', [])
    if not documents:
        state['summary'] = "🔍 No relevant articles found for the given query."
        return state
    
    try:
        summaries = []
        
        for doc in documents:
            source = doc.metadata.get("source", "unknown source")
            chain = summary_prompt | llm | StrOutputParser()
            summary = chain.invoke({"text": doc.page_content, "source": source})
            summaries.append(f"📌 {source} Summary:\n{summary}\n\n🔗 Source: {doc.metadata.get('title', '')}\n{doc.metadata.get('source_url', '')}")
        
        # Format the final summary
        final_summary = f"📚 Article Summaries for: {state['query']}\n\n"
        final_summary += f"🔍 Search Keywords: {state['keywords']}\n\n"
        final_summary += "\n\n".join(summaries)
        
        # Ensure it fits Telegram's limits
        state['summary'] = shorten(final_summary, width=4000, placeholder="... [read full article]")
        
    except Exception as e:
        print(f"Summarization error: {e}")
        state['summary'] = "⚠️ Error generating summary. Please try again."
    
    return state

async def post_to_telegram(state: State) -> State:
    summary = state.get('summary', "No summary available.")
    bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))
    chat_id = os.environ.get("TELEGRAM_CHANNEL_ID")
    try:
        await bot.send_message(chat_id=chat_id, text=summary)
    except Exception as e:
        print(f"Failed to post to Telegram: {e}")
    return state

# Create LangGraph workflow
workflow = StateGraph(State)
workflow.add_node("suggest_keywords", suggest_keywords)
workflow.add_node("search_articles", search_articles)
workflow.add_node("load_articles", load_articles)
workflow.add_node("summarize_articles", summarize_articles)
workflow.add_node("post_to_telegram", post_to_telegram)

# Add edges to define the workflow sequence
workflow.set_entry_point("suggest_keywords")
workflow.add_edge("suggest_keywords", "search_articles")
workflow.add_edge("search_articles", "load_articles")
workflow.add_edge("load_articles", "summarize_articles")
workflow.add_edge("summarize_articles", "post_to_telegram")
workflow.add_edge("post_to_telegram", END)

# Compile the graph
app = workflow.compile()

# Async function to process the user query
async def process_query(query: str) -> Dict:
    initial_state = {"query": query}
    final_state = await app.ainvoke(initial_state)
    return final_state

# Streamlit app for user interaction
st.title("Article Summary Generator For Telegram")
st.markdown("Enter a query to search Wikipedia and Medium, generate summaries, and post to Telegram")

query = st.text_input("🔍 Enter your query:", placeholder="e.g., Machine learning")
if st.button("🚀 Generate and Post Summary"):
    if not query:
        st.warning("Please enter a query first")
    else:
        with st.spinner("⏳ Searching articles and generating summaries..."):
            final_state = asyncio.run(process_query(query))
            
            st.success("✅ Summary posted to Telegram!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🔑 Suggested Keywords")
                st.write(final_state.get("keywords", "No keywords generated."))
            
            with col2:
                st.subheader("🌐 Articles Used")
                if final_state.get("wikipedia_urls"):
                    st.write("**Wikipedia Articles:**")
                    st.write("\n".join([f"- {url}" for url in final_state["wikipedia_urls"]]))
                if final_state.get("medium_urls"):
                    st.write("**Medium Articles:**")
                    st.write("\n".join([f"- {url}" for url in final_state["medium_urls"]]))
            
            st.subheader("📚 Generated Summary")
            st.text_area("Summary", 
                        value=final_state.get("summary", "No summary generated."), 
                        height=400)