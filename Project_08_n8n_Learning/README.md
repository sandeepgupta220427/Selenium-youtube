# Project 08: n8n AI Agent Learning

## Building AI-Powered QA Automation Workflows with n8n

### For QA Engineers & AI Testing Professionals

**The Testing Academy | Author: Dev (Principal SDET & AI Testing Educator)**
**2026 Edition**

---

## 📚 What's Inside

This project covers **5 hands-on n8n projects** that progressively build from a simple AI chatbot to a complete, production-ready AI agent pipeline that reads PRDs, fetches Jira tickets, generates test cases, and writes them to Google Sheets — all automatically.

---

## 🗂️ Projects

| # | Project | Description | Difficulty |
|---|---|---|---|
| 1 | [Basic AI Chat Agent](./Project_01_Basic_AI_Chat/README.md) | Your first n8n AI agent with Groq LLM | 🟢 Beginner |
| 2 | [Test Case Generator (PRD + Jira)](./Project_02_TestGen_PRD_Jira/README.md) | AI agent that reads PRD + Jira to generate test cases | 🟡 Intermediate |
| 3 | [TestGen with Excel Export](./Project_03_TestGen_Excel_Export/README.md) | Full pipeline: PRD + Jira → AI → Google Sheets | 🔴 Advanced |
| 4 | [Jira AI Agent](./Project_04_Jira_AI_Agent/README.md) | Conversational agent that auto-creates Jira tickets | 🟡 Intermediate |
| 5 | [RAG Test Case Pipeline (LangFlow)](./Project_05_RAG_TestCase_LangFlow/README.md) | LangFlow RAG pipeline for test case generation from PDFs | 🔴 Advanced |

---

## 🧠 Shared Resources

- [QA Test Case Generator Prompt (v2)](./Testcase_GEN_prompt_AI_AGENT.md) — The refined system prompt used across agents for generating Jira-compatible test cases.

---

## 🛠️ Prerequisites

- **n8n** installed locally or cloud (Self-hosted recommended: `npx n8n`)
- **Groq API key** (free tier available) — Used as LLM provider
- **Jira Cloud account** — For reading/creating tickets
- **Google Cloud credentials** — For Google Docs and Sheets integration
- **LangFlow** (for Project 5) — `pip install langflow`

---

## 🏗️ Learning Path

```
Project 1 (Basic Chat) → Get comfortable with n8n + AI Agent nodes
        ↓
Project 4 (Jira Agent) → Learn tool-calling: AI → Jira integration
        ↓
Project 2 (PRD + Jira) → Multi-tool agent: read from 2 sources
        ↓
Project 3 (Excel Export) → Full pipeline: read → generate → write
        ↓
Project 5 (RAG Pipeline) → LangFlow: PDF → Vector DB → retrieval
```
