import time
from datetime import datetime
from duckduckgo_search import DDGS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Import Module 2 functionality
from rag import ask_question as module2_ask
from ingestion import ingest_repo

def search_web(query, max_results=3):
    """Performs a web search using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=max_results)
        return list(results)
    except Exception as e:
        return [f"Error performing search: {e}"]

def get_current_time():
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_pdf_report(filename, content):
    """Generates a simple PDF report."""
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        c.drawString(72, height - 72, "AI Agent Report")
        c.drawString(72, height - 100, f"Generated on: {get_current_time()}")
        
        text_object = c.beginText(72, height - 140)
        # Simple text wrapping
        max_width = 80
        lines = []
        for paragraph in content.split('\n'):
            words = paragraph.split()
            current_line = []
            for word in words:
                if len(" ".join(current_line + [word])) < max_width:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            lines.append(" ".join(current_line))
            
        for line in lines:
            text_object.textLine(line)
            
        c.drawText(text_object)
        c.save()
        return f"Successfully created PDF: {filename}"
    except Exception as e:
        return f"Error creating PDF: {e}"

def query_github_rag(repo_name, query, api_key):
    """Wraps Module 2's GitHub RAG."""
    try:
        response, sources = module2_ask(repo_name, query, api_key)
        return f"Github Agent Answer: {response}\nSources: {sources}"
    except Exception as e:
        return f"GitHub Agent Error: {e}"

# Tool Registry
TOOLS = {
    "web_search": search_web,
    "get_time": get_current_time,
    "pdf_report": generate_pdf_report,
    "github_query": query_github_rag
}
