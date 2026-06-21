# 🔍 Findings - Research & Discoveries

> **Project:** Intelligent Test Plan Generator  
> **Status:** Phase 1 - Research Complete  
> **Last Updated:** 2026-02-14

---

## 🧪 Research Summary

### JIRA Integration Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| jira.js | https://github.com/MrRefactoring/jira.js | Official TypeScript wrapper for JIRA Cloud APIs |
| JIRA REST API Docs | Atlassian Developer Portal | Reference for ticket fetching |

**Key Finding:** `jira.js` is the recommended library - production-ready, TypeScript-native, actively maintained.

---

### LLM Integration Resources

#### Groq (Cloud)
| Resource | URL | Purpose |
|----------|-----|---------|
| groq-typescript | https://github.com/groq/groq-typescript | Official Node.js/TypeScript SDK |
| groq-function-calling | https://github.com/hilmanski/groq-function-calling-nodejs | Function calling examples |
| next-groq | https://github.com/Xeven777/next-groq | Chat UI example with Vercel AI SDK |

**Key Finding:** Official SDK supports streaming, multiple models (llama3-70b, mixtral-8x7b), simple integration.

#### Ollama (Local)
| Resource | URL | Purpose |
|----------|-----|---------|
| ollama-js | https://github.com/ollama/ollama-js | Official JavaScript library |
| simple-ollama-chat | https://github.com/jonigl/simple-ollama-chat | React + TypeScript example |
| buni | https://github.com/nanofuxion/buni | Alternative TypeScript client |

**Key Finding:** Ollama has official JS SDK. Can fetch available models via `/api/tags` endpoint.

---

### PDF Parsing Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| pdf-parse (TS) | https://github.com/mehmet-kozan/pdf-parse | Pure TypeScript, cross-platform PDF text extraction |
| pdf.js-extract | https://github.com/ffalt/pdf.js-extract | pdf.js wrapper for Node.js |
| unpdf | https://github.com/unjs/unpdf | Serverless-friendly PDF utilities |

**Key Finding:** `pdf-parse` (mehmet-kozan fork) is pure TypeScript with zero native dependencies - ideal for this project.

---

### Secure Credential Storage

| Resource | URL | Purpose |
|----------|-----|---------|
| node-keytar | https://github.com/atom/node-keytar | Cross-platform OS keychain integration |

**Key Finding:** keytar uses macOS Keychain, Windows Credential Manager, Linux GNOME Keyring. Perfect for storing API tokens securely.

---

### Architecture Decision: Backend Language

| Option | Pros | Cons |
|--------|------|------|
| **Node.js (Express)** | Same language as frontend, npm ecosystem, keytar native support | Callback/Promise mixing |
| **Python (FastAPI)** | Excellent async support, great for LLM/ML tasks | Two language context switching |

**Recommendation:** Node.js (Express) with TypeScript - unified stack, easier maintenance, keytar integration is seamless.

---

## 💡 Key Discoveries

| Date | Finding | Impact |
|------|---------|--------|
| 2026-02-14 | `jira.js` is the best JIRA client | Use for all JIRA API interactions |
| 2026-02-14 | `pdf-parse` (TS fork) has zero native deps | Better compatibility, easier deployment |
| 2026-02-14 | keytar handles cross-platform credential storage | Secure API key storage solved |
| 2026-02-14 | Groq has official TypeScript SDK | Faster integration, type safety |
| 2026-02-14 | Ollama JS SDK supports streaming | Real-time test plan generation possible |

---

## ⚠️ Known Constraints & Limitations

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| keytar requires native compilation | May need build tools on some systems | Provide pre-built binaries or Docker |
| Ollama must be running locally | User must have Ollama installed | Clear setup docs, fallback to Groq |
| PDF parsing may fail on scanned PDFs | Template extraction might not work | Warn users, provide default template |
| JIRA API rate limits | May hit limits with heavy usage | Implement caching, rate limit handling |
| Groq free tier has limits | May need paid key for heavy usage | Document limits, support Ollama fallback |
