# Project 1: Basic AI Chat Agent

## 🟢 Difficulty: Beginner

## Overview

Your first n8n AI agent — a simple conversational chatbot powered by **Groq** (using the Groq LLM API). This is the "Hello World" of n8n AI workflows.

---

## 🎯 What You'll Learn

- Setting up an n8n workflow from scratch
- Using the **Chat Trigger** node (chatTrigger)
- Connecting an **AI Agent** node
- Configuring **Groq Chat Model** as the LLM provider
- Testing the agent via n8n's built-in chat interface

---

## 📋 Flow Diagram

```
┌─────────────────────┐    ┌──────────────┐    ┌──────────────────┐
│ When chat message    │───→│   AI Agent   │←──│  Groq Chat Model  │
│ received             │    │              │    │  (LLM Provider)   │
│ (Chat Trigger)       │    └──────────────┘    └──────────────────┘
└─────────────────────┘
```

---

## 🧩 Nodes Used

| Node | Type | Purpose |
|---|---|---|
| **When chat message received** | `@n8n/n8n-nodes-langchain.chatTrigger` (v1.4) | Provides a chat interface to trigger the workflow |
| **AI Agent** | `@n8n/n8n-nodes-langchain.agent` (v3) | The core AI agent that processes messages and generates responses |
| **Groq Chat Model** | `@n8n/n8n-nodes-langchain.lmChatGroq` (v1) | LLM provider using Groq's API (fast inference) |

---

## 🔧 Setup Instructions

### Step 1: Create the Workflow
1. Open n8n (run `npx n8n` or access your cloud instance).
2. Click **"Add Workflow"** → Name it **"AI_Batch_001"**.

### Step 2: Add the Chat Trigger
1. Search for **"Chat Trigger"** in the node panel.
2. Drag it onto the canvas. No configuration needed — defaults work fine.

### Step 3: Add the AI Agent
1. Search for **"AI Agent"** and add it.
2. Connect **Chat Trigger → AI Agent** (main output to main input).

### Step 4: Add the LLM
1. Search for **"Groq Chat Model"** and add it.
2. Connect it to the AI Agent's **"Language Model"** input.
3. Configure credentials:
   - Go to **Settings → Credentials → Add Credential**
   - Select **Groq API**
   - Paste your Groq API key (get one at [console.groq.com](https://console.groq.com))

### Step 5: Test
1. Click **"Chat"** button in the top-right corner of n8n.
2. Type a message like: *"What are the key principles of software testing?"*
3. The AI agent should respond with a comprehensive answer.

---

## 📥 Import the Flow

Import the pre-built flow directly into n8n:

**[AI_Batch_001.json](../AI_Batch_001.json)**

To import:
1. In n8n, click **"..."** menu → **"Import from File"**
2. Select the JSON file
3. Update your Groq API credential

---

## 🧪 Testing Points

| # | Test | Expected |
|---|---|---|
| 1 | Send a simple greeting | Agent responds conversationally |
| 2 | Ask a QA-specific question | Agent provides a relevant answer |
| 3 | Send a follow-up question | Agent responds (no memory in basic setup) |
| 4 | Send an empty message | Agent handles gracefully |

---

## 🔑 Key Concepts

- **Chat Trigger** creates a webhook-based chat interface — no frontend needed.
- **AI Agent (v3)** is n8n's latest agent node with tool-calling support.
- **Groq** provides extremely fast inference (1000+ tokens/sec) for LLMs like Llama, Mistral, etc.
- This basic setup has **no memory** — each message is independent.

---

**Next:** [Project 2: Test Case Generator (PRD + Jira) →](../Project_02_TestGen_PRD_Jira/)
