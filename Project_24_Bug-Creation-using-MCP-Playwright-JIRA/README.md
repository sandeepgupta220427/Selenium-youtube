# Automated QA & Defect Logging with MCP, Playwright & Jira

This repository demonstrates an end-to-end automated testing workflow using **Playwright** for UI automation, structured test case generation via the **RICE POT method**, and automated defect tracking pushed directly to **Jira** utilizing the Model Context Protocol (MCP).

## 🚀 Features

*   **RICE POT Methodology:** Formalized test cases documented for VWO Login (Validity, Negative scenarios, Internationalization).
*   **Playwright Automation:** Headless/Headed UI testing with automated data input, assertions, and screenshot capturing on failure.
*   **Excel Reporting:** Dynamic aggregation of test outcomes into a consolidated `.xlsx` file (`exceljs`).
*   **Automated Jira Integration:** System-driven instantiation of bugs in Jira, linked to primary stories, paired automatically with failure logs and screenshots via Atlassian's API.
*   **HTML Dashboard:** Comprehensive, stylized single-page HTML report indexing conversation history and results.

## 📐 Architecture Diagram

```mermaid
graph TD;
    Agent[AI Test Automation Agent] -->|Formulates Test Strategy| RICEPOT[RICE POT Test Cases doc];
    Agent -->|Executes Script| Runner(vwo_excel_runner.js);
    Runner -->|Automates Data & Assertions| PW[Playwright Node Container];
    PW -.->|Validates DOM| WebApp[VWO Login System];
    PW -->|Captures Visual Evidence| Screenshot[Failure Screenshot];
    Runner -->|Compiles Results| Excel[Excel Reports];
    Agent -->|Logs Defects via API| Jira[Jira Cloud Backend];
    Screenshot -.->|Attached To| Jira;
    Excel -.->|Attached To| Jira;
    Agent -->|Generates Views| HTML[execution_report.html];
```

## 🔄 Workflow Execution Sequence

```mermaid
sequenceDiagram
    participant Tester as Executor
    participant System as Node Automation Script
    participant Browser as Playwright Chromium
    participant Jira as Atlassian Jira

    Tester->>System: Execute Node Runner
    System->>Browser: Launch Chromium Context
    loop For Each RICE POT Test Case
        System->>Browser: Navigate to Login URI
        Browser-->>System: DOM state fully loaded
        System->>Browser: Inject Credentials (Email/Pass)
        System->>Browser: Emulate 'Sign In' Click
        Browser-->>System: Return DOM State / UI Error Overlays
        alt Test Outcome Meets Expected Goal
            System->>System: Mark as PASS
        else Test Outcome Fails Objective
            System->>Browser: Take Full Page Screenshot
            Browser-->>System: Save PNG
            System->>System: Mark as FAIL
        end
        System->>System: Format & append row to Worksheet
    end
    System->>System: Build array to VWO_Test_Execution_Report.xlsx
    
    System->>Jira: [REST MCP] POST /issue (Bug Details Payload)
    Jira-->>System: Return Bug issueKey (e.g., KAN-10)
    System->>Jira: [REST MCP] POST /issueLink (Link to Main Story)
    System->>Jira: Attach Payload (.xlsx / Screenshot) to Bug
    System-->>Tester: Test Suite complete & Pipeline Logged!
```

## 🛠️ Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/nagarjunabhr8/Bug-Creation-using-MCP-Playwright-JIRA.git
    cd Bug-Creation-using-MCP-Playwright-JIRA
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    npx playwright install chromium
    ```

3.  **Execute the Complete Testing Pipeline:**
    ```bash
    node vwo_excel_runner.js
    ```

*(Note: Direct integration pushes to a live Jira Workspace require local Model Context Protocol definitions `mcp_config.json` supplying authorized cloud API tokens. These keys have been gitignored locally for project security).*
