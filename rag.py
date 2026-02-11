import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from db import get_vector_store

def format_docs(docs):
    return "\n\n".join(f"[Source: {doc.metadata.get('file_path', 'unknown')}]\n{doc.page_content}" for doc in docs)

def ask_question(collection_name: str, query: str, api_key: str):
    """
    Queries the RAG pipeline.
    """
    if not collection_name:
        return "Please ingest a repository first."

    # Initialize LLM
    llm = ChatMistralAI(
        mistral_api_key=api_key,
        model="mistral-tiny", # Efficient model
        temperature=0.2
    )
    
    # Get Retriever
    vector_store = get_vector_store(collection_name)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Simple RAG Prompt
    template = """Answer the question based only on the following context. 
    If you cannot answer the question based on the context, say "I don't find this info in the code".
    
    Context:
    {context}
    
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # RAG Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Retrieve docs separately for sources display
    docs = retriever.invoke(query)
    sources = [doc.metadata.get('file_path') for doc in docs]
    
    # Execute chain
    response = rag_chain.invoke(query)
    
    return response, sources
