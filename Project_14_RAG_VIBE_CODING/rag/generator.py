from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from rag.router import route_question
from rag.ingester import get_vector_store

# Set up the Answer LLM (gpt-4o, Temp=0.3 as per flowchart)
answer_llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

# RAG Answer Prompt
answer_prompt = PromptTemplate.from_template(
    """You are an expert AI testing assistant. Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know. Keep the answer concise and helpful.

Context:
{context}

Question: {question}

Answer:
"""
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def generate_answer(question: str) -> dict:
    """
    1. Routes the question to determine the domain Database.
    2. Queries the specific ChromaDB vector store.
    3. Generates the final answer using GPT-4o.
    """
    
    # 1. Route the question
    domain = route_question(question)
    
    # 2. Get the corresponding Vector Store
    try:
        vector_store = get_vector_store(domain)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    except Exception as e:
        return {"error": f"Failed to access vector store for domain '{domain}'. Error: {e}"}

    # 3. Build the RAG chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | answer_prompt
        | answer_llm
        | StrOutputParser()
    )
    
    # Execute the chain
    answer = rag_chain.invoke(question)
    
    return {
        "domain_routed": domain,
        "answer": answer
    }
