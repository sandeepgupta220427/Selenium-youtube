# Task Plan: Local LLM Testcase Generator

##  Phase 1: Blueprint (Complete)
- [x] **Discovery**: Obtain Testcase Generator Prompt from User (Confirmed).
- [x] **Discovery**: Define A.N.T. Architecture specifics (Streamlit/Python/Ollama).
- [x] **Schema**: Define strict Data Schemas in `gemini.md`.
- [x] **Plan**: Approved. Target Model: `llama3.2`.

## Phase 2: Link (Complete)
- [x] Check if `llama3.2` is installed (`ollama list`) - Verified.
- [x] Pull `llama3.2` if missing (`ollama pull llama3.2`) - Present.
- [x] Create `test_connection.py` to verify API is responsive - Success.

## Phase 3: Architect (Current)
- [ ] **A (Adapter)**: Create `ollama_client.py` (Wrapper for Ollama).
- [ ] **N (Nexus)**: Create `generator_logic.py` (Prompt engineering & strict parser).
- [ ] **T (Template)**: Create `app.py` (Streamlit UI).
- [ ] API Design.

## Phase 4: Stylize
- [ ] Frontend Development.

## Phase 5: Trigger
- [ ] Testing & Validation.
