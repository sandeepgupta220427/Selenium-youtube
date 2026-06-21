# Project 3: TestGen with Excel Export (Full Pipeline)

## 🔴 Difficulty: Advanced

## Overview

The **complete end-to-end pipeline**: The AI agent reads a PRD from Google Docs, fetches Jira ticket details, generates structured test cases using a refined v2 prompt, and **automatically writes the test cases to a Google Sheets spreadsheet**. This is a production-grade workflow.

---

## 🎯 What You'll Learn

- Building a **4-tool AI agent** (read PRD + read Jira + write to Sheets + memory)
- Using **Google Sheets Tool** for structured data output
- Adding **Window Buffer Memory** for conversational context
- Crafting a **production-grade v2 system prompt** with guardrails
- Understanding n8n's column mapping with `$fromAI()` expressions

---

## 📋 Flow Diagram

```
┌─────────────────────┐    ┌──────────────────────────────────────────┐
│ When chat message    │───→│              AI Agent                    │
│ received             │    │                                          │
│ (Public Chat Trigger)│    │   System Prompt: v2.0 Production-Grade   │
└─────────────────────┘    │                                          │
                            │   Tools:                                 │
                            │   ├── READ_JIRA (Jira Tool)              │
                            │   ├── READ_PRD (Google Docs Tool)        │
                            │   └── Update to Sheet (Google Sheets)    │
                            │                                          │
                            │   Memory: Simple Memory (Buffer Window)  │
                            │   LLM: Groq (openai/gpt-oss-120b)       │
                            └──────────────────────────────────────────┘
```

---

## 🧩 Nodes Used

| Node | Type | Purpose |
|---|---|---|
| **When chat message received** | `chatTrigger` (v1.4, **public**) | Public chat interface |
| **AI Agent** | `agent` (v3) | Core agent with v2 system prompt |
| **BRAIN** (Groq Chat Model) | `lmChatGroq` (v1) | LLM: `openai/gpt-oss-120b` |
| **READ_JIRA** | `jiraTool` (v1) | Reads Jira ticket by Issue Key |
| **READ_PRD** | `googleDocsTool` (v2) | Reads PRD from Google Docs |
| **Update to Sheet** | `googleSheetsTool` (v4.7) | Writes test cases to Google Sheets |
| **Simple Memory** | `memoryBufferWindow` (v1.3) | Retains conversation context |

---

## 📊 Google Sheets Column Mapping

The agent writes test cases directly to a Google Sheet with this structure:

| Column | AI Expression | Description |
|---|---|---|
| Test Case ID / Jira ID | `$fromAI('Test_Case_ID__Jira_ID')` | Unique test case ID (matching key) |
| Module/Feature | `$fromAI('Module_Feature')` | Feature under test |
| Test Case Title | `$fromAI('Test_Case_Title')` | Descriptive title starting with "Verify..." |
| Preconditions | `$fromAI('Preconditions')` | System state before test |
| Test Steps | `$fromAI('Test_Steps')` | Numbered steps (1. 2. 3.) |
| Test Data | `$fromAI('Test_Data')` | Concrete test values |
| Expected Result | `$fromAI('Expected_Result')` | Observable, measurable outcome |
| Priority | `$fromAI('Priority')` | Critical / High / Medium / Low |
| Test Type | `$fromAI('Test_Type')` | Functional / Negative / Boundary / etc. |

The sheet uses **"Append or Update"** mode with the **Test Case ID / Jira ID** column as the matching key — so re-running the same request updates existing rows rather than creating duplicates.

---

## 🔧 Setup Instructions

### Step 1: Set Up Google Sheets
1. Create a new Google Sheet.
2. Add these headers in Row 1:
   ```
   Test Case ID  Jira ID | Module/Feature | Test Case Title | Preconditions | Test Steps | Test Data | Expected Result | Priority | Test Type
   ```
3. Share the sheet with your Google Cloud service account.

### Step 2: Configure Credentials
1. **Groq API** — Your Groq API key
2. **Jira Software Cloud** — Email + API token + domain
3. **Google Docs OAuth2** — For reading the PRD
4. **Google Sheets OAuth2** — For writing test cases

### Step 3: Update the Flow
1. Import `AI_Batch_003_TestGen_Creator_Our_PRD_Excel.json`
2. Update the **READ_PRD** node with your PRD document URL
3. Update the **Update to Sheet** node with your Google Sheet URL
4. Connect all credentials

### Step 4: Test
```
Create test cases for Jira ID BW-456 — User Registration feature
```

The agent will:
1. Read the PRD from Google Docs
2. Fetch the Jira ticket
3. Generate test cases using the v2 prompt
4. Write each test case as a row in Google Sheets

---

## 📝 System Prompt v2 Highlights

This project uses a significantly enhanced prompt compared to Project 2:

### New in v2:
- **Expanded test categories**: Security, Performance (in addition to Functional, Negative, etc.)
- **Priority assignment logic**: Clear rules for Critical/High/Medium/Low
- **Zero Hallucination Policy**: Every test case must trace to a documented requirement
- **Ambiguity Flagging**: Ambiguous ACs are flagged as gaps with conditional expected results
- **Completeness Check**: After generating, verify every AC has at least one mapped test case
- **No Duplicate Coverage**: Each behavior tested exactly once
- **Concrete test data**: No placeholders like "valid input" — must use actual values

---

## 📥 Import the Flow

Import the pre-built flow: **[AI_Batch_003_TestGen_Creator_Our_PRD_Excel.json](../AI_Batch_003_TestGen_Creator_Our_PRD_Excel.json)**

---

## 🧪 Testing Points

| # | Test | Expected |
|---|---|---|
| 1 | Full pipeline execution | Test cases appear in Google Sheet |
| 2 | Re-run with same Jira ID | Existing rows are updated, not duplicated |
| 3 | Multiple test case generation | Each test case is a separate row |
| 4 | Memory persistence | Follow-up "add more edge cases" retains context |
| 5 | Gap identification | Agent flags missing ACs before generating |
| 6 | Priority accuracy | Critical bugs → Critical, UI polish → Low |
| 7 | Output format compliance | All columns populated with concrete data |

---

## 🔑 Key Concepts

- **Window Buffer Memory** lets the agent remember previous messages in the conversation — you can say "add more negative cases" and it remembers the context.
- **Google Sheets as output** makes the test cases immediately actionable — the team can review, comment, and import to Jira directly.
- **`appendOrUpdate` mode** with matching columns prevents duplicates on re-execution.
- **Public chat trigger** (`public: true`) allows sharing the chat URL with team members.

---

**Next:** [Project 4: Jira AI Agent →](../Project_04_Jira_AI_Agent/)
