from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

class RouteQuery(BaseModel):
    """Route a user query to the most relevant domain database."""
    target_domain: str = Field(
        ...,
        description="The target domain for the query. Choose exactly one from: 'api', 'ui', or 'perf'. Defaults to 'api' if unsure."
    )

def setup_router():
    """Initializes the LLM and the structured output for routing."""
    # Using gpt-4o-mini with Temp=0 as per flowchart specification
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(RouteQuery)
    return structured_llm

router_prompt = PromptTemplate.from_template(
    """You are an intelligent routing assistant for an AI testing system.
Your job is to classify the user's question into one of three domains:

1. 'api': For questions concerning backend structure, API endpoints, testing APIs, payloads, API docs, etc.
2. 'ui': For questions concerning frontend testing, user interface structures, DOM elements, Playwright/Selenium specifics, UI forms, etc.
3. 'perf': For questions concerning application performance, load testing, response times, memory leaks, JMeter/K6, etc.

Analyze the question carefully and return the appropriate domain code. If you are extremely unsure, default to 'api'.

Question: {question}
"""
)

def route_question(question: str) -> str:
    """
    Takes a user question and returns the string code representing the domain Database:
    'api', 'ui', or 'perf'.
    """
    router_llm = setup_router()
    chain = router_prompt | router_llm
    result = chain.invoke({"question": question})
    
    domain = result.target_domain.lower()
    
    # Fallback safety guard
    if domain not in ["api", "ui", "perf"]:
        domain = "api"
        
    return domain
