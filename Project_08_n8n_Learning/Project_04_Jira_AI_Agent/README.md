# Project 4: Jira AI Agent (Conversational Ticket Creator)

## 🟡 Difficulty: Intermediate

## Overview

A conversational AI agent that **automatically creates Jira tickets** from natural language chat messages. Tell the agent about a bug or feature request in plain English, and it creates a properly formatted Jira ticket in your project.

---

## 🎯 What You'll Learn

- Using the **Jira Tool in "Create" mode** (vs. "Read" mode in Projects 2/3)
- Adding **Window Buffer Memory** for multi-turn conversations
- Understanding **LLM provider options**: Groq, OpenAI, and Anthropic (with fallback)
- How `$fromAI()` enables the AI to fill in Jira ticket fields dynamically

---

## 📋 Flow Diagram

```
                 Objective: If user chats, Agent will
                 create the JIRA Ticket automatically

┌─────────────────────┐    ┌──────────────────────────────────────────┐
│ When chat message    │───→│              AI Agent                    │
│ received             │    │                                          │
│ (Chat Trigger)       │    │   Tools:                                 │
└─────────────────────┘    │   └── Create Issue in Jira Software      │
                            │       ├── Project: VWO Project           │
                            │       ├── Issue Type: Bug                │
                            │       ├── Summary: $fromAI('Summary')    │
                            │       └── Description: $fromAI('Desc')   │
                            │                                          │
                            │   Memory: Simple Memory (Buffer Window)  │
                            │   LLM: Groq (openai/gpt-oss-120b)       │
                            │                                          │
                            │   (Disabled: OpenAI GPT-4.1-mini)        │
                            │   (Disabled: Claude Sonnet 4.5)          │
                            └──────────────────────────────────────────┘
```

---

## 🧩 Nodes Used

| Node | Type | Purpose |
|---|---|---|
| **When chat message received** | `chatTrigger` (v1.4) | Chat interface |
| **AI Agent** | `agent` (v3) | Processes messages and decides to create tickets |
| **Brain** (Groq Chat Model) | `lmChatGroq` (v1) | LLM: `openai/gpt-oss-120b` (active) |
| **OpenAI Chat Model** | `lmChatOpenAi` (v1.3) | GPT-4.1-mini (disabled, available as fallback) |
| **Anthropic Chat Model** | `lmChatAnthropic` (v1.3) | Claude Sonnet 4.5 (disabled, available as fallback) |
| **Simple Memory** | `memoryBufferWindow` (v1.3) | Retains conversation context |
| **Create Issue in Jira Software** | `jiraTool` (v1) | Creates Bug tickets in VWO Project |

---

## 🔧 Setup Instructions

### Step 1: Configure Jira Tool
The Jira tool is pre-configured to create **Bug** tickets in the **VWO Project**:
- **Project**: VWO Project (ID: 10033) — Change this to your project
- **Issue Type**: Bug (ID: 10042) — Change to your issue type ID
- **Summary**: Dynamically filled by the AI via `$fromAI('Summary')`
- **Description**: Dynamically filled by the AI via `$fromAI('Description')`

### Step 2: Set Up LLM
Three LLM options are included (Groq is active, others disabled):
- **Groq** (recommended for speed): Uses `openai/gpt-oss-120b`
- **OpenAI**: GPT-4.1-mini (enable if you prefer OpenAI)
- **Anthropic**: Claude Sonnet 4.5 (enable for best quality)

> Only **one** LLM should be active at a time. Disable the others.

### Step 3: Add Credentials
1. **Groq API** (or OpenAI/Anthropic depending on your choice)
2. **Jira Software Cloud API** — Email + API token

### Step 4: Test
```
I found a bug on the login page. When I enter an email with special 
characters like test+user@gmail.com, it shows "Invalid email" even 
though it's a valid email format. This affects the user registration 
flow. Priority is high.
```

The agent will create a Jira ticket with:
- **Summary**: "Login page rejects valid emails with special characters"
- **Description**: Detailed bug description with steps, expected vs actual behavior

---

## 📥 Import the Flow

Import the pre-built flow: **[JIRA AI Agent.json](../JIRA%20AI%20Agent.json)**

---

## 🧪 Testing Points

| # | Test | Expected |
|---|---|---|
| 1 | Describe a bug in natural language | Jira ticket created with proper summary + description |
| 2 | Describe a feature request | Ticket created (may need to change issue type) |
| 3 | Ask a general question (not a bug) | Agent responds without creating a ticket |
| 4 | Follow-up with additional details | Memory retains context, can update the description |
| 5 | Ambiguous message | Agent asks for clarification before creating |
| 6 | Check created ticket in Jira | Verify summary and description are well-formatted |

---

## 🔑 Key Concepts

- **Tool-calling pattern**: The AI agent doesn't always create a ticket. It uses reasoning to decide **when** to call the Jira tool vs. just responding conversationally.
- **`$fromAI()` for write operations**: Unlike reading (where the tool returns data), here the AI **generates** the field values (summary, description) and the tool writes them to Jira.
- **Multi-LLM setup**: Having multiple LLMs configured (with some disabled) makes it easy to switch providers without rebuilding the workflow.
- **Window Buffer Memory**: The agent remembers the conversation, so you can incrementally provide more context: "Actually, also mention it happens on Chrome only."

---

## ⚠️ Important Notes

- The Jira project ID and issue type ID are **hardcoded** in the flow. You must update these to match your Jira instance.
- To find your project ID: Go to your Jira project → Settings → Details → look for the project key.
- To find issue type IDs: Use the Jira REST API: `GET /rest/api/3/issuetype`

---

**Next:** [Project 5: RAG Test Case Pipeline (LangFlow) →](../Project_05_RAG_TestCase_LangFlow/)
