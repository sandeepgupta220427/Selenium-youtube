# 📋 Task Plan: Selenium to Playwright Converter

Project: Selenium to Playwright Javascript/Typescript converter

## 🗺️ Phases

### Phase 0: Initialization 🟢
- [x] Create project memory files (`task_plan.md`, `findings.md`, `progress.md`, `gemini.md`)
- [ ] Define Project Constitution in `gemini.md`
- [x] Answer Discovery Questions
- [x] Define JSON Data Schema in `gemini.md`
- [x] Research existing conversion patterns (TestNG Java -> Playwright JS/TS)
- [x] Finalize Blueprint:
    - **Engine**: Hybrid approach (Java Parser + LLM).
    - **Parsing**: Use `java-parser` to extract class/method/annotation metadata.
    - **Conversion**: Pass metadata + code blocks to LLM with strict mapping SOP.
    - **Verification**: Basic syntax check on output.

### Phase 2: Link (Connectivity) ⚡
- [x] Setup local LLM connectivity (Ollama)
- [x] Verify API/LLM responses (Handshake successful)
- [x] Setup environment variables (`.env`)

### Phase 3: Architect (The 3-Layer Build) ⚙️
- [x] **Layer 1: Architecture**: Create technical SOPs in `architecture/` (conversion_sop.md)
- [x] **Layer 2: Navigation**: Implement decision-making logic (converter_engine.ts)
- [x] **Layer 3: Tools**: Create atomic scripts in `tools/` (parser, llm_client, trigger)
- [x] **Verification**: Successfully converted sample Java to Playwright using codellama.

### Phase 4: Stylize (Refinement & UI) ✨
- [x] Payload Refinement (Handled by LLM SOP)
- [x] UI/UX for the converter tool (React + Premium CSS)
- [ ] Final feedback and polishing

---
## 🎯 Goals
- Convert Selenium Java (TestNG) code to Playwright (JS/TS) code.
- Source: User UI input.
- Output: UI display + local directory storage.
- Mapping: Strict 1:1 functional mapping.
