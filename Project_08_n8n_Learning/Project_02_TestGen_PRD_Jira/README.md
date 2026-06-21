# Project 2: Test Case Generator (PRD + Jira)

## 🟡 Difficulty: Intermediate

## Overview

An AI agent that **reads a Product Requirement Document (PRD)** from Google Docs and **fetches Jira ticket details**, then generates structured, Jira-compatible test cases. This is the first multi-tool agent — the AI decides which tools to call and when.

---

## 🎯 What You'll Learn

- Building a **multi-tool AI agent** that calls different tools based on context
- Using **Jira Tool** to read ticket details (acceptance criteria, description)
- Using **Google Docs Tool** to read a PRD document
- Crafting a **system prompt** that enforces structured output
- Understanding n8n's `$fromAI()` expressions for dynamic tool parameters

---

## 📋 Flow Diagram

```
┌─────────────────────┐    ┌──────────────────────────────────────────┐
│ When chat message    │───→│              AI Agent                    │
│ received             │    │                                          │
│ (Chat Trigger)       │    │   System Prompt:                         │
└─────────────────────┘    │   "Senior QA Engineer with 15+ years..." │
                            │                                          │
                            │   Tools:                                 │
                            │   ├── READ_JIRA (Jira Tool)              │
                            │   └── READ_PRD (Google Docs Tool)        │
                            │                                          │
                            │   LLM: Groq (openai/gpt-oss-120b)       │
                            └──────────────────────────────────────────┘
```

---

## 🧩 Nodes Used

| Node | Type | Purpose |
|---|---|---|
| **When chat message received** | `chatTrigger` (v1.4) | Chat interface trigger |
| **AI Agent** | `agent` (v3) | Core agent with system prompt |
| **BRAIN** (Groq Chat Model) | `lmChatGroq` (v1) | LLM: `openai/gpt-oss-120b` via Groq |
| **READ_JIRA** | `jiraTool` (v1) | Reads Jira ticket by Issue Key |
| **READ_PRD** | `googleDocsTool` (v2) | Reads PRD from Google Docs URL |

---

## 🔧 Setup Instructions

### Step 1: Set Up Credentials
1. **Groq API** — Add your Groq API key.
2. **Jira Software Cloud** — Connect using email + API token:
   - Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Create an API token
   - In n8n, add a Jira credential with your email + token + domain
3. **Google Docs OAuth2** — Connect your Google account (needs Docs read access).

### Step 2: Configure the Nodes
1. **READ_JIRA**: Uses dynamic parameter `$fromAI('Issue_Key')` — the AI agent will pass the Jira ID automatically.
2. **READ_PRD**: Points to your Google Docs PRD URL.
3. **AI Agent**: Contains a detailed system prompt (see below).

### Step 3: Test
Send a message like:
```
Create test cases for app.bw.com for Jira ID BW-123
```

The agent will:
1. Fetch the Jira ticket BW-123 to read acceptance criteria
2. Fetch the PRD from Google Docs
3. Generate structured test cases in Jira-compatible table format

---

## 📝 System Prompt (Key Sections)

The system prompt instructs the agent to:

1. **Step 1 — Read Sources Only**: Extract features, acceptance criteria, business rules from PRD and Jira. No hallucination allowed.
2. **Step 2 — Test Case Design**: Cover positive, negative, boundary, field validation, error handling, integration scenarios.
3. **Step 3 — Output Format**: Strict Jira tabular format with columns:

| Test Case ID | Jira ID | Module/Feature | Test Case Title | Preconditions | Test Steps | Test Data | Expected Result | Priority | Test Type |

### Critical Rules
- 🚫 Do NOT hallucinate
- 🚫 Do NOT create requirements
- ✅ Each test case must be **atomic** (one behavior)
- ✅ Each test case must be **traceable** to Jira acceptance criteria
- ✅ Expected results must be **measurable**

---

## 📥 Import the Flow

Import the pre-built flow: **[AI_Batch_002_Test_PRD_JIRA_ID.md](../AI_Batch_002_Test_PRD_JIRA_ID.md)**

> **Note:** Despite the `.md` extension, this file contains the n8n JSON workflow. Import it directly into n8n.

---

## 🧪 Testing Points

| # | Test | Expected |
|---|---|---|
| 1 | Valid Jira ID + PRD exists | Structured table of test cases |
| 2 | Invalid Jira ID | Agent reports it cannot fetch the ticket |
| 3 | PRD has missing acceptance criteria | Agent flags gaps before generating |
| 4 | Ask for specific test types only | "Generate negative tests for BW-123" works |
| 5 | Output format compliance | Table has all 10 required columns |

---

## 🔑 Key Concepts

- **`$fromAI()`** expressions let the AI agent dynamically fill in tool parameters. The agent "decides" what Jira ID to look up based on the user's message.
- **Google Docs Tool** provides read-only access to shared documents — no manual copy-paste needed.
- The **system prompt** is critical — it constrains the AI to only use documented sources, preventing hallucination.

---

**Next:** [Project 3: TestGen with Excel Export →](../Project_03_TestGen_Excel_Export/)
