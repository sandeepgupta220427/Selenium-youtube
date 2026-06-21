"""
Integration patterns showing how to feed different input sources into DeepEval.
Used by the /integrations page.
"""

INTEGRATIONS = {
    "rag_pipeline": {
        "name": "RAG Pipeline",
        "icon": "&#x1F4DA;",
        "color": "blue",
        "description": "Evaluate a retrieval-augmented generation pipeline end-to-end — retriever + generator together.",
        "when_to_use": "Your app queries a vector DB, gets chunks, and asks an LLM to answer from them.",
        "input_flow": [
            {"step": "User Query", "desc": "The question being asked", "color": "accent"},
            {"step": "Embedding", "desc": "Query -> vector", "color": "blue"},
            {"step": "Vector DB", "desc": "ChromaDB / Pinecone / Weaviate", "color": "blue"},
            {"step": "Retrieved Chunks", "desc": "Top-K relevant docs", "color": "blue"},
            {"step": "LLM Generation", "desc": "Answer from chunks", "color": "purple"},
            {"step": "LLMTestCase", "desc": "query + output + context", "color": "accent"},
            {"step": "DeepEval Metrics", "desc": "RAG Triad scores", "color": "green"},
        ],
        "recommended_metrics": ["contextual_relevancy", "faithfulness", "answer_relevancy", "contextual_precision", "contextual_recall"],
        "code_example": '''# RAG Pipeline Evaluation
from chromadb import Client
from openai import OpenAI
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, ContextualRelevancyMetric

def evaluate_rag(query: str):
    # 1. Retrieve from vector DB
    chroma = Client()
    collection = chroma.get_collection("docs")
    results = collection.query(query_texts=[query], n_results=3)
    chunks = results["documents"][0]

    # 2. Generate answer
    llm = OpenAI()
    response = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer from context: {chunks}"},
            {"role": "user", "content": query},
        ],
    )
    answer = response.choices[0].message.content

    # 3. Build test case and run RAG Triad
    test_case = LLMTestCase(
        input=query,
        actual_output=answer,
        retrieval_context=chunks,
    )

    for metric_cls in [ContextualRelevancyMetric, FaithfulnessMetric, AnswerRelevancyMetric]:
        m = metric_cls(threshold=0.7, model="gpt-4o-mini")
        m.measure(test_case)
        print(f"{m.__class__.__name__}: {m.score:.2f}")

evaluate_rag("What is your return policy?")''',
    },

    "chatbot_pipeline": {
        "name": "Chatbot Pipeline",
        "icon": "&#x1F916;",
        "color": "purple",
        "description": "Evaluate a live chatbot API by calling it with test questions and scoring responses.",
        "when_to_use": "You have a deployed chatbot (FastAPI / LangChain / custom) with an HTTP endpoint.",
        "input_flow": [
            {"step": "User Query", "desc": "Test question", "color": "accent"},
            {"step": "HTTP POST", "desc": "POST /chat {message}", "color": "yellow"},
            {"step": "Chatbot API", "desc": "FastAPI / Flask server", "color": "purple"},
            {"step": "Response JSON", "desc": "reply + context", "color": "purple"},
            {"step": "LLMTestCase", "desc": "build from response", "color": "accent"},
            {"step": "DeepEval Metrics", "desc": "Multi-metric scoring", "color": "green"},
        ],
        "recommended_metrics": ["answer_relevancy", "faithfulness", "hallucination", "bias", "toxicity"],
        "code_example": '''# Chatbot API Evaluation
import requests
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric

CHATBOT_URL = "http://localhost:8100/chat"

def ask_chatbot(question: str) -> dict:
    resp = requests.post(CHATBOT_URL, json={"message": question})
    return resp.json()

def evaluate_chatbot(question: str):
    # 1. Call the chatbot API
    result = ask_chatbot(question)

    # 2. Build test case from response
    test_case = LLMTestCase(
        input=question,
        actual_output=result["reply"],
        retrieval_context=result["retrieval_context"],
    )

    # 3. Run the 5-metric quality gate
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),
        FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini"),
        HallucinationMetric(threshold=0.5, model="gpt-4o-mini"),
    ]
    for m in metrics:
        m.measure(test_case)
        status = "PASS" if m.score >= m.threshold else "FAIL"
        print(f"{m.__class__.__name__}: {m.score:.2f} [{status}]")

evaluate_chatbot("What is your refund policy?")''',
    },

    "voice_input": {
        "name": "Voice Input",
        "icon": "&#x1F3A4;",
        "color": "yellow",
        "description": "Evaluate voice-driven apps. Transcribe speech to text, then score the LLM response.",
        "when_to_use": "Voice assistants, IVR bots, Alexa/Siri-style apps, call center LLMs.",
        "input_flow": [
            {"step": "Audio Input", "desc": ".wav / .mp3 / mic", "color": "yellow"},
            {"step": "Whisper / STT", "desc": "Speech-to-text", "color": "yellow"},
            {"step": "Transcribed Query", "desc": "Text string", "color": "accent"},
            {"step": "LLM Processing", "desc": "Answer generation", "color": "purple"},
            {"step": "LLMTestCase", "desc": "transcript + output", "color": "accent"},
            {"step": "DeepEval Metrics", "desc": "Including STT accuracy", "color": "green"},
        ],
        "recommended_metrics": ["answer_relevancy", "faithfulness", "toxicity", "bias"],
        "code_example": '''# Voice Input Evaluation
from openai import OpenAI
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, GEval

client = OpenAI()

def transcribe(audio_file_path: str) -> str:
    with open(audio_file_path, "rb") as audio:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
        )
    return result.text

def evaluate_voice(audio_file: str, expected_intent: str):
    # 1. Transcribe audio to text
    query = transcribe(audio_file)
    print(f"Transcribed: {query}")

    # 2. Send to LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
    )
    answer = response.choices[0].message.content

    # 3. Build test case
    test_case = LLMTestCase(
        input=query,
        actual_output=answer,
        expected_output=expected_intent,
    )

    # 4. Score answer + STT-specific GEval for intent capture
    relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
    intent_match = GEval(
        name="Intent Capture",
        criteria="Does the transcript preserve the user\\'s intent despite any STT noise?",
        evaluation_params=["input", "expected_output"],
        threshold=0.7,
        model="gpt-4o-mini",
    )

    for m in [relevancy, intent_match]:
        m.measure(test_case)
        print(f"{m.name if hasattr(m, \\'name\\') else m.__class__.__name__}: {m.score:.2f}")

evaluate_voice("customer_call.wav", "User wants to return an order")''',
    },

    "ai_agent": {
        "name": "AI Agent Calling Evaluation",
        "icon": "&#x1F9E0;",
        "color": "green",
        "description": "Evaluate agentic systems — agents that call tools, use memory, and execute multi-step plans.",
        "when_to_use": "CrewAI, LangChain agents, AutoGen, custom tool-calling LLMs.",
        "input_flow": [
            {"step": "User Goal", "desc": "Multi-step task", "color": "accent"},
            {"step": "Agent Planner", "desc": "Decides tool calls", "color": "green"},
            {"step": "Tool Executions", "desc": "API calls, DB, search", "color": "yellow"},
            {"step": "Multi-turn Trace", "desc": "Conversation + tools", "color": "purple"},
            {"step": "ConversationalTestCase", "desc": "turns + tool calls", "color": "accent"},
            {"step": "DeepEval Metrics", "desc": "Role + Knowledge + Tool use", "color": "green"},
        ],
        "recommended_metrics": ["answer_relevancy", "faithfulness", "bias", "toxicity"],
        "code_example": '''# AI Agent Evaluation (with tool calls + multi-turn)
from crewai import Agent, Task, Crew
from deepeval.test_case import ConversationalTestCase, Turn
from deepeval.metrics import (
    KnowledgeRetentionMetric,
    RoleAdherenceMetric,
    ConversationCompletenessMetric,
)

def evaluate_agent(user_goal: str):
    # 1. Run the agent (CrewAI example)
    researcher = Agent(
        role="QA Researcher",
        goal="Find and summarize info",
        backstory="You help users by searching and summarizing.",
    )
    task = Task(description=user_goal, agent=researcher)
    crew = Crew(agents=[researcher], tasks=[task])
    result = crew.kickoff()

    # 2. Build conversational test case from agent trace
    convo = ConversationalTestCase(
        chatbot_role="A QA research assistant.",
        turns=[
            Turn(role="user", content=user_goal),
            Turn(role="assistant", content=str(result)),
        ],
    )

    # 3. Evaluate agent-specific metrics
    metrics = [
        KnowledgeRetentionMetric(threshold=0.7, model="gpt-4o-mini"),
        RoleAdherenceMetric(threshold=0.7, model="gpt-4o-mini"),
        ConversationCompletenessMetric(threshold=0.7, model="gpt-4o-mini"),
    ]
    for m in metrics:
        m.measure(convo)
        print(f"{m.__class__.__name__}: {m.score:.2f}")

evaluate_agent("Summarize the refund policy and list 3 key points")''',
    },
}
