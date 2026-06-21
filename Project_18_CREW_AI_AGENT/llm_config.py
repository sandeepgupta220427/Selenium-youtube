"""
Reusable LLM configuration for CrewAI agents.

Usage:
    from llm_config import get_llm
    llm = get_llm()  # uses LLM_PROVIDER from .env (default: ollama)
    llm = get_llm("groq")  # override provider
"""

import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

# Default models per provider
DEFAULT_MODELS = {
    "ollama": "ollama/llama3.2",
    "groq": "groq/llama-3.3-70b-versatile",
    "openai": "openai/gpt-4o-mini",
}


def get_llm(provider: str | None = None, model: str | None = None) -> LLM:
    """
    Create and return a CrewAI LLM instance.

    Args:
        provider: LLM provider ("ollama", "groq", "openai").
                  Defaults to LLM_PROVIDER env var, then "ollama".
        model:    Override the default model for the provider.

    Returns:
        Configured CrewAI LLM instance.
    """
    provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()
    model = model or os.getenv("LLM_MODEL") or DEFAULT_MODELS.get(provider)

    if not model:
        raise ValueError(f"No default model for provider '{provider}'. Pass a model explicitly.")

    if provider == "ollama":
        llm = LLM(
            model=model,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("Set a valid GROQ_API_KEY in your .env file")
        llm = LLM(model=model, api_key=api_key)
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("Set a valid OPENAI_API_KEY in your .env file")
        llm = LLM(model=model, api_key=api_key)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            f"Supported: {', '.join(DEFAULT_MODELS.keys())}"
        )

    print(f"✅ LLM configured: provider={provider}, model={model}")
    return llm
