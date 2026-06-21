# 🤖 CrewAI — QA Test Case Generator

An AI-powered **test case generator** built with [CrewAI](https://www.crewai.com/) and [Ollama](https://ollama.com/). This project uses a multi-agent framework to automatically generate structured QA test cases for application features — starting with a login page example.

---

## 📖 Project Overview

This project demonstrates how to use **CrewAI** to create an autonomous AI agent that acts as a **Senior QA Engineer**. The agent analyzes a given feature (e.g., a login page) and produces detailed test cases with titles, steps, and expected/actual results.

### How It Works

The project follows the core CrewAI pattern:

```
LLM (Brain) → Agent (QA Engineer) → Task (Generate Test Cases) → Crew (Orchestrator) → Output
```

| Component | Description |
|-----------|-------------|
| **LLM** | `ollama/llama3.2:1b` running locally via Ollama |
| **Agent** | A Senior QA Engineer with 15 years of experience |
| **Task** | Generate 5 test cases for a login page (email + password) |
| **Crew** | Orchestrates the agent and task execution |

### Project Structure

```
Project 15 - Crew-AI/
├── .env                 # Environment variables (Ollama URL, API keys)
├── .venv/               # Python virtual environment
├── testcase_crew.py     # Main script — CrewAI agent that generates QA test cases
├── test_llm.py          # Utility script — Quick test to verify LLM connectivity
└── README.md            # This file
```

### File Descriptions

- **`testcase_crew.py`** — The main application. Defines a QA Engineer agent, assigns it a test-case-generation task, assembles a Crew, and kicks off execution.
- **`test_llm.py`** — A lightweight script to verify that the Ollama LLM is reachable and responding correctly.
- **`.env`** — Stores the `Ollama_URL` and `GROQ_API_KEY` environment variables.

---

## ⚙️ Prerequisites

Before you begin, make sure you have the following installed:

| Tool | Minimum Version | Check Command |
|------|----------------|---------------|
| **Python** | 3.10+ | `python --version` |
| **pip** | Latest | `pip --version` |
| **Ollama** | Latest | `ollama --version` |

> [!IMPORTANT]
> **Ollama** must be installed and running locally since this project uses `ollama/llama3.2:1b` as the LLM backend. Download it from [https://ollama.com/download](https://ollama.com/download).

---

## 🚀 Installation

### Step 1 — Clone or Navigate to the Project

```bash
cd "c:\Users\Naveen\Naveen Ravichandran - AI\AI_Projects\Project 15 - Crew-AI"
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

```bash
# Windows (CMD)
.\.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

### Step 3 — Install CrewAI and Dependencies

```bash
pip install crewai python-dotenv
```

> [!TIP]
> To install CrewAI with all optional tools and integrations, use:
> ```bash
> pip install 'crewai[tools]'
> ```

### Step 4 — Pull the Ollama Model

Make sure Ollama is running, then pull the required model:

```bash
ollama pull llama3.2:1b
```

### Step 5 — Configure Environment Variables

Create or verify the `.env` file in the project root:

```env
Ollama_URL=http://localhost:11434
GROQ_API_KEY=your_groq_api_key_here
```

---

## ✅ Verifying the Installation

### Check 1 — Verify Python Packages

```bash
pip show crewai
```

Expected output (version may vary):

```
Name: crewai
Version: x.x.x
Summary: ...
```

You can also list all installed CrewAI-related packages:

```bash
pip list | findstr crewai
```

### Check 2 — Verify Ollama is Running

```bash
ollama list
```

You should see `llama3.2:1b` in the list of available models.

### Check 3 — Test LLM Connectivity

Run the LLM test script to confirm the model responds:

```bash
python test_llm.py
```

✅ **Expected**: A short greeting response from the LLM (e.g., *"Hello! How can I help you today?"*).

❌ **If it fails**: Make sure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3.2:1b`).

---

## ▶️ Execution

### Running the Test Case Generator

```bash
python testcase_crew.py
```

### What to Expect

1. The script loads environment variables from `.env`
2. Initializes the LLM connection to Ollama (`llama3.2:1b`)
3. Creates a **QA Engineer** agent
4. Assigns it a task: *Generate 5 test cases for a login page*
5. The **Crew** orchestrates the execution
6. The agent outputs **5 structured test cases** to the console

### Sample Output Format

Each test case will include:

```
Test Case #1
─────────────
Title:       Successful login with valid credentials
Steps:       1. Navigate to login page
             2. Enter valid email
             3. Enter valid password
             4. Click the Login button
Expected:    User is redirected to the dashboard
Actual:      [To be filled during testing]
```

> [!NOTE]
> Since verbose mode is enabled (`verbose=True`), you will see detailed logs of the agent's reasoning process in the terminal. This is useful for debugging and understanding how the AI agent thinks.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'crewai'` | Run `pip install crewai` inside your virtual environment |
| `Connection refused` to Ollama | Start Ollama with `ollama serve` |
| Model not found | Pull the model: `ollama pull llama3.2:1b` |
| `.env` not loading | Ensure `python-dotenv` is installed: `pip install python-dotenv` |
| Slow response | The `1b` model is lightweight; consider `llama3.2:3b` for better quality |

---

## 🛠️ Tech Stack

- **[CrewAI](https://www.crewai.com/)** — Multi-agent orchestration framework
- **[Ollama](https://ollama.com/)** — Local LLM runtime
- **[LLaMA 3.2 (1B)](https://ollama.com/library/llama3.2)** — Meta's lightweight language model
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — Environment variable management

---

## 📄 License

This project is for educational and personal use.
