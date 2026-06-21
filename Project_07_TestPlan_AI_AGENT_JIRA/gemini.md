# 📜 Project Constitution - gemini.md

> **Project:** Intelligent Test Plan Generator  
> **Status:** Phase 1 - Data Schemas Defined  
> **Last Updated:** 2026-02-14

---

## 🏛️ Architectural Invariants

These rules must never be violated:

1. **Reliability Over Speed:** All automation must be deterministic and self-healing
2. **3-Layer Architecture:** Strict separation between Architecture, Navigation, and Tools
3. **Data-First:** JSON schemas must be defined before any code is written
4. **No Guessing:** Business logic must be explicitly defined, never assumed
5. **Security First:** API keys never touch frontend, always encrypted at rest

---

## 📊 Data Schemas

### Schema 1: JIRA Configuration (Settings)
```json
{
  "baseUrl": "https://company.atlassian.net",
  "username": "user@company.com",
  "apiToken": "[encrypted - stored via keytar]"
}
```

### Schema 2: LLM Configuration (Settings)
```json
{
  "provider": "groq|ollama",
  "groq": {
    "apiKey": "[encrypted - stored via keytar]",
    "model": "llama3-70b-8192|mixtral-8x7b-32768|gemma2-9b-it",
    "temperature": 0.7
  },
  "ollama": {
    "baseUrl": "http://localhost:11434",
    "model": "llama3.1|codellama|mistral"
  }
}
```

### Schema 3: Template Metadata
```json
{
  "id": "uuid-v4",
  "name": "Standard Test Plan",
  "fileName": "testplan.pdf",
  "filePath": "/templates/testplan.pdf",
  "extractedText": "# Test Plan Template\n\n## Overview...",
  "uploadedAt": "2026-02-14T12:00:00Z",
  "isDefault": true
}
```

### Schema 4: JIRA Ticket (API Response)
```json
{
  "key": "VWO-123",
  "summary": "Add user login functionality",
  "description": "As a user, I want to log in...",
  "priority": "High|Medium|Low",
  "status": "In Progress|To Do|Done",
  "assignee": {
    "email": "john.doe@company.com",
    "displayName": "John Doe"
  },
  "labels": ["frontend", "auth", "critical"],
  "acceptanceCriteria": [
    "User can enter email and password",
    "Session persists for 24 hours",
    "Error message on invalid credentials"
  ],
  "attachments": [
    {
      "filename": "mockup.png",
      "contentType": "image/png",
      "size": 102456
    }
  ],
  "createdAt": "2026-01-15T10:00:00Z",
  "updatedAt": "2026-02-10T14:30:00Z"
}
```

### Schema 5: Test Plan Generation Request
```json
{
  "ticketId": "VWO-123",
  "templateId": "uuid-v4",
  "provider": "groq|ollama",
  "model": "llama3-70b-8192"
}
```

### Schema 6: Generated Test Plan (Output)
```json
{
  "id": "uuid-v4",
  "ticketId": "VWO-123",
  "ticketSummary": "Add user login functionality",
  "templateId": "uuid-v4",
  "templateName": "Standard Test Plan",
  "provider": "groq",
  "model": "llama3-70b-8192",
  "generatedAt": "2026-02-14T12:09:11Z",
  "content": "# Test Plan: Add user login functionality\n\n## Overview\n...",
  "wordCount": 1250,
  "generationTimeMs": 4500
}
```

### Schema 7: Generation History (Database)
```json
{
  "id": "uuid-v4",
  "ticketId": "VWO-123",
  "ticketSummary": "Add user login functionality",
  "generatedAt": "2026-02-14T12:09:11Z",
  "provider": "groq",
  "model": "llama3-70b-8192",
  "preview": "# Test Plan...",
  "fullContentPath": "/data/testplans/uuid-v4.md"
}
```

---

## 🎭 Behavioral Rules

### System Personality
- Professional and concise QA/Engineering tone
- Prioritizes clarity over cleverness
- Validates all assumptions
- Proactive error reporting with actionable suggestions

### Do Not Rules
- Do NOT write scripts in `tools/` before Discovery is complete
- Do NOT assume business logic without confirmation
- Do NOT skip the handshake verification in Phase 2
- Do NOT store API keys in localStorage or frontend code
- Do NOT proceed with generation if connection test fails
- Do NOT allow unvalidated PDF uploads (max 5MB)

### Input Validation Rules
- JIRA ID: Must match regex `^[A-Z][A-Z0-9]*-\d+$`
- URLs: Must be valid HTTPS URLs
- PDF files: Max 5MB, must be valid PDF format
- Temperature: Must be between 0.0 and 1.0

### Error Handling Rules
- Timeout: 30s for Groq, 120s for Ollama
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
- Graceful degradation: Clear error messages with suggestions
- Fallback: If LLM fails, suggest checking model availability

### UX Guidelines
- Loading states for all async operations
- Progress indicators for multi-step workflows
- Toast notifications for success/error feedback
- Keyboard shortcuts: Ctrl+Enter (generate), Ctrl+Shift+S (save)

---

## 🔌 Integration Requirements

| Service | Purpose | Credentials Status | Library |
|---------|---------|-------------------|---------|
| JIRA REST API v3 | Fetch ticket data | User-provided | `jira.js` |
| Groq API | Cloud LLM | User-provided | `groq-sdk` |
| Ollama | Local LLM | Self-hosted | `ollama` (JS SDK) |
| OS Keychain | Secure storage | System-native | `keytar` |
| SQLite | Local database | Auto-initialized | `better-sqlite3` |

---

## 📁 Directory Structure

```
intelligent-test-plan-agent/
├── BLAST.md                    # Framework reference
├── gemini.md                   # Project Constitution (this file)
├── task_plan.md                # Phases and checklists
├── findings.md                 # Research and discoveries
├── progress.md                 # Activity log
├── .env.example                # Environment variables template
├── docker-compose.yml          # Optional Docker setup
│
├── /frontend                   # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── forms/         # Settings forms
│   │   │   └── jira-display/  # Ticket display components
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── History.tsx
│   │   ├── hooks/
│   │   │   ├── useJira.ts
│   │   │   ├── useLLM.ts
│   │   │   └── useTemplates.ts
│   │   └── services/
│   │       ├── api.ts
│   │       └── storage.ts
│   └── package.json
│
├── /backend                    # Node.js + Express + TypeScript
│   ├── src/
│   │   ├── routes/
│   │   │   ├── settings.ts
│   │   │   ├── jira.ts
│   │   │   ├── llm.ts
│   │   │   └── templates.ts
│   │   ├── services/
│   │   │   ├── jira-client.ts
│   │   │   ├── llm-providers/
│   │   │   │   ├── groq-provider.ts
│   │   │   │   └── ollama-provider.ts
│   │   │   ├── pdf-parser.ts
│   │   │   └── secure-storage.ts
│   │   ├── utils/
│   │   │   ├── encryption.ts
│   │   │   ├── validators.ts
│   │   │   └── errors.ts
│   │   └── database/
│   │       ├── schema.sql
│   │       └── db.ts
│   └── package.json
│
├── /architecture               # Layer 1: Technical SOPs
│   ├── 01-jira-integration.md
│   ├── 02-llm-integration.md
│   ├── 03-template-processing.md
│   └── 04-generation-workflow.md
│
├── /tools                      # Layer 3: Atomic scripts
│   └── (to be created in Phase 3)
│
├── /templates                  # Default test plan templates
│   └── default-testplan.pdf
│
├── /data                       # Runtime data (SQLite, etc.)
│   └── app.db
│
└── .tmp                        # Intermediate file operations
    └── (temporary files)
```

---

## ✅ Phase 1 Approval Checklist

- [x] Discovery Questions answered
- [x] Data schemas defined
- [x] Research completed
- [ ] User approval of Blueprint
- [ ] Ready to proceed to Phase 2 (Link)

---

## 🎯 Success Criteria (from requirements)

1. User can input JIRA credentials and successfully fetch ticket "VWO-1"
2. User can upload `testplan.pdf` and system extracts structure
3. User can generate test plan using both Groq (cloud) and Ollama (local) modes
4. Generated content follows template structure while incorporating JIRA specifics
5. All API keys persist securely between sessions
