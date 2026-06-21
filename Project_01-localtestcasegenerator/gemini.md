# Project Constitution (gemini.md)

## 1. Data Schemas
### Test Case Object (JSON)
```json
{
  "id": "TC-001",
  "title": "String",
  "description": "String",
  "preconditions": ["String"],
  "steps": ["String"],
  "expected_result": "String",
  "priority": "High | Medium | Low",
  "type": "Functional | Boundary | Negative"
}
```

## 2. Behavioral Rules
- **Reliability > Speed**: Do not optimize prematurely; ensure correctness.
- **No Guessing**: Ask for clarification if business logic is ambiguous.
- **Self-Healing**: Scripts should detect failures and attempt recovery or report clearly.
- **Strict JSON**: All LLM outputs must be validated against the Schema.

## 3. Architectural Invariants (A.N.T.)
- **A (Adapter)**: `ollama_client.py` - Wraps `ollama` python library. Handles connection retries.
- **N (Nexus)**: `generator_logic.py` - Manages prompts, parsing, and JSON validation.
- **T (Template)**: `app.py` (Streamlit/FastAPI) - The User Interface for input/output.

