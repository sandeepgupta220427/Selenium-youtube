# Technical SOP: Local Test Case Generation

## Goal
Generate structured software test cases from unstructured user input using a local Ollama LLM (`llama3.2`).

## Inputs
- **User Prompt** (String): Requirement description or code snippet.
- **Model**: `llama3.2` (default).

## Output Schema (Strict JSON)
Returns a list of `TestCase` objects:
```json
[
  {
    "id": "TC-XYZ",
    "title": "Short Summary",
    "description": "Detailed explanation",
    "preconditions": ["List of preconditions"],
    "steps": ["Step 1", "Step 2"],
    "expected_result": "Outcome",
    "priority": "High | Medium | Low",
    "type": "Functional | Negative | Boundary"
  }
]
```

## Logic Flow
1.  **Receive Input**: Accept raw text from User UI.
2.  **Construct Prompt**: Wrap input in the "System Prompt" (defined in `prompts.py` or logic).
    *   *Constraint*: Must explicitly demand valid JSON output.
3.  **Call LLM**: Invoke `ollama.chat`.
4.  **Parse/Validate**:
    *   Strip markdown fences (```json ... ```).
    *   Load JSON.
    *   Validate against `TestCase` schema.
5.  **Return**: Valid JSON or Error Message.

## Edge Cases
- **Invalid JSON**: The model returns text instead of strict JSON. -> *Action*: Retry once, then fail gracefully.
- **Model Offline**: Ollama not running. -> *Action*: Raise connection error.
