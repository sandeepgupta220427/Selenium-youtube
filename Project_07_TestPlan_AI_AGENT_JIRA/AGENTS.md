# 🤖 Project 7: TestPlan AI Agent JIRA

**Identity:** This project implements the **B.L.A.S.T. Protocol** for building deterministic, self-healing automation systems that integrate with JIRA for test plan management.

---

## 📋 Project Overview

This project is part of the **AI Tester Blueprint** course series. It uses the B.L.A.S.T. (Blueprint, Link, Architect, Stylize, Trigger) protocol combined with the A.N.T. 3-layer architecture to create an AI-powered test plan management system integrated with JIRA.

**Core Philosophy:**
- Prioritize reliability over speed
- Never guess at business logic
- LLMs are probabilistic; business logic must be deterministic

---

## 🏗️ Architecture

### B.L.A.S.T. Protocol

| Phase | Name | Purpose |
|-------|------|---------|
| **B** | Blueprint | Vision & Logic - Discovery, Data Schema, Research |
| **L** | Link | Connectivity - API verification, credential testing |
| **A** | Architect | 3-Layer Build - SOPs, Navigation, Tools |
| **S** | Stylize | Refinement & UI - Payload formatting, UX polish |
| **T** | Trigger | Deployment & Execution |

### A.N.T. 3-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Navigation (Decision Making)                       │
│ - Reasoning layer that routes data between SOPs and Tools   │
│ - Calls execution tools in the right order                  │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Architecture (architecture/)                       │
│ - Technical SOPs written in Markdown                        │
│ - Define goals, inputs, tool logic, edge cases              │
│ - Golden Rule: Update SOP before updating code              │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Tools (tools/)                                     │
│ - Deterministic Python scripts                              │
│ - Atomic and testable                                       │
│ - Environment variables in .env                             │
│ - Intermediate files in .tmp/                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Project7-TestPlan_AI_AGENT_JIRA/
├── architecture/          # Technical SOPs (Markdown)
│   └── (Create SOPs here)
├── tools/                 # Deterministic Python scripts
│   └── (Create tool scripts here)
├── .tmp/                  # Intermediate file operations
├── .env                   # Environment variables and tokens
├── gemini.md              # Project Constitution (Data schemas, rules, invariants)
├── task_plan.md           # Phases, goals, and checklists
├── findings.md            # Research, discoveries, constraints
├── progress.md            # What was done, errors, tests, results
├── BLAST.md               # B.L.A.S.T. Protocol Reference
└── AGENTS.md              # This file
```

---

## 🔧 Technology Stack

| Category | Technology |
|----------|------------|
| **Protocol** | B.L.A.S.T. (Blueprint, Link, Architect, Stylize, Trigger) |
| **Architecture** | A.N.T. 3-Layer (Architecture, Navigation, Tools) |
| **Backend** | Python |
| **Integration** | JIRA API |
| **Documentation** | Markdown |

---

## 🚀 Development Workflow

### Protocol 0: Initialization (Mandatory)

Before any code is written or tools are built:

1. **Initialize Project Memory**
   - Create `task_plan.md` → Phases, goals, and checklists
   - Create `findings.md` → Research, discoveries, constraints
   - Create `progress.md` → What was done, errors, tests, results
   - Initialize `gemini.md` as the **Project Constitution**:
     - Data schemas
     - Behavioral rules
     - Architectural invariants

2. **Halt Execution**
   - Strictly forbidden from writing scripts in `tools/` until:
     - Discovery Questions are answered
     - Data Schema is defined in `gemini.md`
     - `task_plan.md` has an approved Blueprint

### Phase 1: Blueprint (Vision & Logic)

**Discovery Questions:**
1. **North Star:** What is the singular desired outcome?
2. **Integrations:** Which external services (JIRA, etc.) do we need? Are keys ready?
3. **Source of Truth:** Where does the primary data live?
4. **Delivery Payload:** How and where should the final result be delivered?
5. **Behavioral Rules:** How should the system "act"? (Tone, logic constraints, "Do Not" rules)

**Data-First Rule:**
- Define the **JSON Data Schema** (Input/Output shapes) in `gemini.md`
- Coding only begins once the "Payload" shape is confirmed

**Research:**
- Search GitHub repos and other databases for helpful resources

### Phase 2: Link (Connectivity)

1. **Verification:** Test all API connections and `.env` credentials
2. **Handshake:** Build minimal scripts in `tools/` to verify external services respond correctly
3. Do not proceed to full logic if the "Link" is broken

### Phase 3: Architect (The 3-Layer Build)

**Layer 1: Architecture (`architecture/`)**
- Write Technical SOPs in Markdown
- Define goals, inputs, tool logic, and edge cases
- **Golden Rule:** If logic changes, update the SOP before updating the code

**Layer 2: Navigation (Decision Making)**
- Reasoning layer that routes data between SOPs and Tools
- Do not perform complex tasks directly; call execution tools in the right order

**Layer 3: Tools (`tools/`)**
- Deterministic Python scripts
- Atomic and testable
- Store environment variables/tokens in `.env`
- Use `.tmp/` for all intermediate file operations

### Phase 4: Stylize (Refinement & UI)

1. **Payload Refinement:** Format all outputs (Slack blocks, Notion layouts, Email HTML) for professional delivery
2. **UI/UX:** If the project includes a dashboard or frontend, apply clean CSS/HTML and intuitive layouts
3. **Feedback:** Present stylized results to the user for feedback before final deployment

---

## 📝 Code Style Guidelines

### Python Scripts (tools/)

- Write deterministic, atomic functions
- Each tool should have a single responsibility
- Include type hints for function signatures
- Add docstrings describing:
  - Purpose
  - Input parameters
  - Output/return value
  - Edge cases

### Markdown SOPs (architecture/)

- Use clear, structured headers
- Include input/output specifications
- Document edge cases and error handling
- Provide examples where applicable

### Project Memory Files

| File | Purpose |
|------|---------|
| `gemini.md` | Project Constitution - Data schemas, behavioral rules, architectural invariants |
| `task_plan.md` | Phases, goals, and checklists |
| `findings.md` | Research, discoveries, constraints |
| `progress.md` | What was done, errors, tests, results |

---

## 🧪 Testing Strategy

1. **Unit Testing:** Each tool in `tools/` should be independently testable
2. **Integration Testing:** Verify API connections during the Link phase
3. **End-to-End Testing:** Test the complete workflow from input to JIRA output
4. **Error Handling:** Document all error cases in SOPs and handle gracefully

---

## 🔐 Security Considerations

- Store all credentials in `.env` file (never commit to version control)
- Use `.gitignore` to exclude `.env`, `.tmp/`, and sensitive files
- Validate all inputs before processing
- Sanitize data before sending to external APIs
- Log sensitive operations without exposing credentials

---

## 🚫 Do Not Rules

1. Do not write scripts in `tools/` until Discovery Questions are answered
2. Do not write scripts in `tools/` until Data Schema is defined in `gemini.md`
3. Do not write scripts in `tools/` until `task_plan.md` has an approved Blueprint
4. Do not guess at business logic
5. Do not commit `.env` files
6. Do not store intermediate files outside `.tmp/`

---

## 📚 References

- **B.L.A.S.T. Protocol:** See `BLAST.md` for complete protocol reference
- **AI Tester Blueprint:** Parent course series for context
- **JIRA API Documentation:** For integration details

---

<div align="center">

**Built with the B.L.A.S.T. Protocol**

*Deterministic automation for reliable test plan management*

</div>
