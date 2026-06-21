-- Settings table for app configuration
CREATE TABLE IF NOT EXISTS settings (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  jira_base_url TEXT,
  jira_username TEXT,
  llm_provider TEXT DEFAULT 'groq',
  groq_model TEXT DEFAULT 'openai/gpt-oss-120b',
  groq_temperature REAL DEFAULT 0.7,
  ollama_base_url TEXT DEFAULT 'http://localhost:11434',
  ollama_model TEXT DEFAULT 'llama3.1',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Templates table for storing test plan templates
CREATE TABLE IF NOT EXISTS templates (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  file_name TEXT,
  file_path TEXT,
  extracted_text TEXT,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_default BOOLEAN DEFAULT 0
);

-- Generation history table
CREATE TABLE IF NOT EXISTS generation_history (
  id TEXT PRIMARY KEY,
  ticket_id TEXT NOT NULL,
  ticket_summary TEXT,
  template_id TEXT,
  template_name TEXT,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  preview TEXT,
  full_content_path TEXT,
  word_count INTEGER,
  generation_time_ms INTEGER,
  FOREIGN KEY (template_id) REFERENCES templates(id)
);

-- Recent tickets cache
CREATE TABLE IF NOT EXISTS recent_tickets (
  ticket_id TEXT PRIMARY KEY,
  ticket_summary TEXT,
  ticket_data TEXT,
  fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default template
INSERT OR IGNORE INTO templates (id, name, file_name, extracted_text, is_default) 
VALUES (
  'default-testplan',
  'Default Test Plan Template',
  null,
  '# Test Plan

## Overview
Brief description of the feature being tested.

## Scope
### In Scope
- Feature components to be tested
- User scenarios covered

### Out of Scope
- Features explicitly not tested
- Known limitations

## Test Strategy
### Test Levels
- Unit Testing
- Integration Testing
- System Testing
- User Acceptance Testing

### Test Types
- Functional Testing
- Regression Testing
- Performance Testing
- Security Testing
- Usability Testing

## Test Cases

### Test Case 1: [Title]
**ID:** TC001
**Priority:** High/Medium/Low
**Preconditions:** Required setup
**Steps:**
1. Step one
2. Step two
3. Step three
**Expected Result:** What should happen
**Actual Result:** (To be filled during execution)
**Status:** Pass/Fail/Blocked

## Entry Criteria
- Prerequisites for testing to begin

## Exit Criteria
- Conditions for testing to be considered complete

## Risks and Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| Risk description | High/Medium/Low | Mitigation strategy |

## Deliverables
- Test Plan Document
- Test Cases
- Test Execution Report
- Defect Reports',
  1
);

-- Insert default settings
INSERT OR IGNORE INTO settings (id) VALUES (1);
