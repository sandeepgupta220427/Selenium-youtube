## [6.8.0] - 2026-03-02 - "Productivity Boost & In-App Sync"

> **Major productivity enhancements to existing skills and new in-app skill synchronization feature.**

This release delivers version 2.0.0 upgrades to two critical skills: `vibe-code-auditor` and `tutorial-engineer`, packed with pattern recognition shortcuts, deterministic scoring, and copy-paste templates. Plus, a new "Sync Skills" button in the Web App enables live skill updates from GitHub without leaving the browser.

## 🚀 New Features

### 🔄 In-App Sync Skills Button

**One-click skill synchronization from the Web App UI.**
Replaces the unreliable START_APP.bat auto-updater. Users can now click "Sync Skills" in the web app to download the latest skills from GitHub instantly.

- Vite dev server plugin exposing `/api/refresh-skills` endpoint
- Downloads and extracts only the `/skills/` folder and `skills_index.json`
- Live UI updates without page refresh

## 📦 Improvements

### ✨ vibe-code-auditor v2.0.0

**Productivity-focused overhaul with 10x faster audits.**

- **Pattern Recognition Shortcuts**: 10 heuristics for rapid issue detection
- **Quick Checks**: 3-second scans for each of 7 audit dimensions
- **Executive Summary**: Critical findings upfront
- **Deterministic Scoring**: Replaces subjective ranges with algorithmic scoring
- **Code Fix Blocks**: Before/after examples for copy-paste remediation
- **Quick Wins Section**: Fixes completable in <1 hour
- **Calibration Rules**: Scoring adjusted by code size (snippet vs multi-file)
- **Expanded Security**: SQL injection, path traversal, insecure deserialization detection

### 📚 tutorial-engineer v2.0.0

**Evidence-based learning with 75% better retention.**

- **4-MAT Model**: Why/What/How/What If framework for explanations
- **Learning Retention Shortcuts**: Evidence-based patterns (+75% retention)
- **Cognitive Load Management**: 7±2 rule, One Screen, No Forward References
- **Exercise Calibration**: Difficulty table with time estimates
- **Format Selection Guide**: Quick Start vs Deep Dive vs Workshop
- **Pre-Publish Audit Checklist**: Comprehension, progression, technical validation
- **Speed Scoring Rubric**: 1-5 rating on 5 dimensions
- **Copy-Paste Template**: Ready-to-use Markdown structure
- **Accessibility Checklist**: WCAG compliance for tutorials

## 👥 Credits

A huge shoutout to our community contributors:

- **@munir-abbasi** for the v2.0.0 productivity enhancements to `vibe-code-auditor` and `tutorial-engineer` (PR #172)
- **@zinzied** for the In-App Sync Skills Button and START_APP.bat simplification (PR #178)

---

_Upgrade now: `git pull origin main` to fetch the latest skills._
