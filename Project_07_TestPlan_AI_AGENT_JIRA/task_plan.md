# 🎯 Task Plan - BLAST Framework

> **Project:** Intelligent Test Plan Generator (Full-Stack Web Application)  
> **Status:** Phase 1 - Blueprint (In Progress)  
> **Last Updated:** 2026-02-14

---

## 📋 Phase Checklist

### Phase 0: Initialization ✅ COMPLETE
- [x] Create `task_plan.md`
- [x] Create `findings.md`
- [x] Create `progress.md`
- [x] Initialize `gemini.md` (Project Constitution)

### Phase 1: Blueprint (Vision & Logic) 🔄 IN PROGRESS
- [x] Discovery: Answer 5 key questions
- [x] Define JSON Data Schema in `gemini.md`
- [x] Research: GitHub repos and resources
- [ ] Approve Blueprint (awaiting user confirmation)

### Phase 2: Link (Connectivity) ⏳ PENDING
- [ ] Verify JIRA API connections
- [ ] Test Groq API connections
- [ ] Test Ollama API connections
- [ ] Build handshake verification scripts

### Phase 3: Architect (3-Layer Build) ⏳ PENDING
- [ ] Layer 1: Create architecture SOPs
- [ ] Layer 2: Build navigation/decision layer
- [ ] Layer 3: Develop atomic tools in `tools/`

### Phase 4: Stylize (Refinement & UI) ⏳ PENDING
- [ ] Payload refinement for outputs
- [ ] UI/UX polish
- [ ] Gather feedback

### Phase 5: Trigger (Deployment) ⏳ PENDING
- [ ] Final testing
- [ ] Deployment
- [ ] Documentation

---

## 🎯 Project Summary

### North Star
Build a full-stack web application that **automates test plan creation** by integrating JIRA ticket data with LLM-powered analysis using customizable PDF templates.

### Integrations Required
| Service | Purpose | Status |
|---------|---------|--------|
| JIRA REST API v3 | Fetch ticket data | User-provided credentials |
| Groq API | Cloud LLM provider | User-provided API key |
| Ollama | Local LLM provider | Self-hosted |

### Tech Stack
- **Frontend:** React (Vite) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend:** Node.js (Express) or Python (FastAPI) - *to be decided*
- **Storage:** SQLite (settings/history) + File system (templates)
- **Security:** OS keychain via keytar for credential storage

---

## 📝 Notes

- Prioritize reliability over speed
- Never guess at business logic
- Follow A.N.T. 3-layer architecture
- API keys must be encrypted, never in localStorage
