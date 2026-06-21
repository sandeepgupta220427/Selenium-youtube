# 1. LangFlow Quick-Start Guide

## What is LangFlow?

LangFlow is a visual builder for LLM applications. Instead of writing everything in Python first, you connect components on a canvas:

- input nodes
- prompt nodes
- model nodes
- tool nodes
- memory nodes
- retrievers
- outputs

It is especially useful for QA engineers because you can prototype:

- simple chatbots
- prompt chains
- QA assistants
- tool-using agents
- RAG pipelines
- evaluation and routing flows

Before jumping into RAG, it is better to understand the Langflow basics first.

---

## Installation

```bash
# Install LangFlow
pip install langflow

# Launch LangFlow
langflow run

# Or use Docker
docker run -p 7860:7860 langflowai/langflow:latest

# Open in browser
http://localhost:7860
```

---

## What Else Can LangFlow Do?

RAG is only one use case. LangFlow can also help you build:

| Area | What you can build |
|---|---|
| Basic chat apps | Simple chatbots with Groq, OpenAI, Ollama, Anthropic |
| Prompt chains | Structured prompt -> model -> output pipelines |
| QA assistants | Domain-specific assistants for testing, support, documentation |
| Test design helpers | Test case generators, bug-to-test converters, requirement-to-test workflows |
| Tool-based agents | Agents that use calculator, APIs, search, SQL, MCP tools |
| Routers | Route requests by topic, domain, or intent |
| Memory flows | Chat history and session-aware assistants |
| RAG systems | Vector search + prompt grounding |
| Custom logic | Python-based custom components inside LangFlow |
| API serving | Expose flows as endpoints and call them from apps |

---

## Important LangFlow Features

These are the features beginners should know before building RAG:

1. `Canvas-based building`
Connect nodes visually and inspect the data flow step by step.

2. `Playground testing`
You can run the flow directly in the built-in chat/playground UI.

3. `Execution trace`
LangFlow shows what each node received and produced. This is one of the best features for debugging.

4. `Reusable components`
Prompt templates, models, tools, routers, and retrievers can be reused across many flows.

5. `Custom components`
If a built-in node is missing, you can create your own Python-powered component.

6. `Import and export`
Flows can be shared as JSON files and imported into another LangFlow instance.

7. `API endpoints`
A flow can be exposed and called programmatically from your app or test framework.

8. `Multi-model support`
You are not locked into one provider. You can switch between Groq, OpenAI, Ollama, and others.

---

## Core Building Blocks

When you look at a LangFlow project, think in terms of these building blocks:

| Block | Example components | Purpose |
|---|---|---|
| Input | `Chat Input`, `File`, `Directory` | Bring data into the flow |
| Prompt | `Prompt Template` | Structure the instructions sent to the model |
| Model | `Groq`, `OpenAI`, `Ollama` | Generate text or reasoning |
| Tool | `Calculator`, `MCPTools`, search tools | Give the model actions |
| Router | `Smart Router`, `Conditional Router` | Send inputs down different branches |
| Data processing | `Type Convert`, splitters | Transform data between steps |
| Retrieval | `Chroma`, `FAISS`, retrievers | Fetch relevant knowledge |
| Output | `Chat Output`, text outputs | Show the final response |

---

## How to Think About Your First Flows

Start in this order:

1. `Simple chat`
Learn how input, model, and output work.

2. `API + review workflow`
Learn how LangFlow can call an external system such as Jira, normalize raw data, and generate useful QA artifacts.

3. `Prompt-based assistant`
Learn how prompts shape the response.

4. `Prompt-based mini app`
Learn how to turn one strong prompt into a practical workflow such as a test case generator.

5. `Tool-based agent`
Learn how models can act, not just answer.

6. `RAG`
Only after the above makes sense, add document loading, chunking, embeddings, and retrieval.

---

## Four QA Starter Agents

Inside this QuickStart, the 4 most important QA-oriented LangFlow starter agents are:

1. `RICE-POT test case generator`
Import: [rice_pot_testcase_generator_langflow.json](./rice_pot_testcase_generator_langflow.json)

2. `Jira ticket -> test plan + test cases`
Import: [jira_ticket_testplan_langflow.json](./jira_ticket_testplan_langflow.json)

3. `Jira story score -> HTML report`
Import: [jira_story_score_html_agent_langflow.json](./jira_story_score_html_agent_langflow.json)

4. `PDF -> JSON agent`
Import: [pdf_to_json_agent_langflow.json](./pdf_to_json_agent_langflow.json)

These 4 flows give you practical QA automation patterns before you move into RAG.

---

## Example 1: Simple Chatbot with Groq

This is the fastest possible useful LangFlow app.

### Goal

Build a chatbot using `Groq` and `Chat Input`.

### Nodes to Add

- `Chat Input`
- `Groq`
- `Chat Output`

### Connections

```text
Chat Input -> Groq -> Chat Output
```

### Groq Configuration

In the `Groq` node:

- add your Groq API key
- model: `llama-3.1-8b-instant`
- temperature: `0.2`

### What to Test

Try prompts like:

- `Explain what API testing is in simple words.`
- `What is the difference between smoke and regression testing?`
- `List 5 test cases for a login page.`

### What You Learn Here

- how `Chat Input` works
- how a model node generates a response
- how to use the playground
- how to inspect output quickly

---

## Example 2: Fetch Jira Ticket and Generate Test Plan + Test Cases

This is the second beginner workflow. It shows how LangFlow can pull structured data from Jira and turn it into useful QA outputs.

### Goal

Fetch a Jira ticket using the Jira REST API, review the story content, and generate:

- a short test plan
- a test case set

### Importable JSON

You can import this ready-made Langflow starter flow:

- [jira_ticket_testplan_langflow.json](./jira_ticket_testplan_langflow.json)

### Nodes to Add

- `API Request`
- `Parser`
- `Groq`
- `Prompt Template`
- `Groq`
- `Chat Output`

### Connections

```text
API Request -> Parser -> Groq (review) -> Prompt Template -> Groq (generation) -> Chat Output
```

### What Each Node Does

1. `API Request`
Calls Jira REST API and fetches the issue payload.

2. `Parser`
Converts the raw API response into a clean text block for the first LLM.

3. `Groq` (review)
Reads the raw Jira payload and extracts a usable story summary, description, acceptance criteria, risks, and gaps.

4. `Prompt Template`
Takes that reviewed story and asks for two outputs: a test plan and test cases.

5. `Groq` (generation)
Generates the final QA content.

6. `Chat Output`
Displays the final result.

### API Request Setup

In the `API Request` node:

- method: `GET`
- URL: `https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123`
- headers:
  - `Accept: application/json`
  - `Authorization: Basic <base64_email_colon_api_token>`

### Parser Setup

Use `Parser` mode with a template like:

```text
Jira API Source: {source}
HTTP Status: {status_code}
API Error: {error}

Jira Ticket Payload:
{result}
```

### Review LLM Setup

Use the first `Groq` node to review the Jira payload.

Recommended settings:

- model: `llama-3.3-70b-versatile`
- temperature: `0`

Its job is to convert raw Jira JSON into:

- issue key
- summary
- description
- acceptance criteria
- priority
- labels
- dependencies
- risks
- open questions

### Final Prompt Setup

The `Prompt Template` takes the reviewed Jira story as a variable such as `userStory` and asks for:

- `Section 1: Test Plan`
- `Section 2: Test Cases`

The test cases should be returned in a markdown table.

### Final Generation LLM Setup

Use the second `Groq` node for final generation.

Recommended settings:

- model: `llama-3.3-70b-versatile`
- temperature: `0.1`

### What to Test

- update the API Request node to a valid Jira ticket in your Jira Cloud project
- run the flow and verify that the Jira story is summarized clearly
- check that the output contains both a test plan and execution-ready test cases

### What You Learn Here

- how to integrate LangFlow with a real REST API
- how to normalize raw JSON before final generation
- how to turn Jira stories into QA planning artifacts

---

## Example 3: Simple QA Assistant with Prompt Template

Now add a prompt layer so the assistant behaves like a QA mentor instead of a general chatbot.

### Goal

Build a small assistant for software testing questions.

### Nodes to Add

- `Chat Input`
- `Prompt Template`
- `Groq`
- `Chat Output`

### Connections

```text
Chat Input -> Prompt Template -> Groq -> Chat Output
```

### Prompt Template

Use something like:

```text
You are a senior QA mentor.
Answer the user's question clearly and practically.
If relevant, include:
- testing type
- example test cases
- common mistakes

Question:
{question}

Answer:
```

### Prompt Variable

Create one variable in the prompt:

- `question`

Connect `Chat Input` to that field.

### Recommended Groq Settings

- model: `llama-3.1-8b-instant`
- temperature: `0`

### What to Test

- `How do I write test cases for password reset?`
- `What should I validate in a checkout flow?`
- `How do I test file upload functionality?`

### What You Learn Here

- how prompt templates control behavior
- how to turn a raw chat model into a role-based assistant
- why prompt engineering matters before RAG

---

## Example 4: Basic Test Case Generator with RICE-POT

This is a practical beginner workflow. It turns a strong prompt framework into a reusable QA app.

### Goal

Build a simple test case generator using the same `RICE-POT` method used in `Project_03_RICE_POT_PROMPT_SeleniumFramework`, but adapted for test design instead of framework code generation.

### Importable JSON

You can import this ready-made Langflow starter flow:

- [rice_pot_testcase_generator_langflow.json](./rice_pot_testcase_generator_langflow.json)

### Nodes to Add

- `Chat Input`
- `Prompt Template`
- `Groq`
- `Chat Output`

### Connections

```text
Chat Input -> Prompt Template -> Groq -> Chat Output
```

### Prompt Variable

Use one variable:

- `input`

Connect `Chat Input` to the `input` field in the prompt.

### Prompt Design

The prompt uses the `RICE-POT` structure:

- `R` = Role
- `I` = Instructions
- `C` = Context
- `E` = Example
- `P` = Parameters
- `O` = Output
- `T` = Tone

In this flow, the prompt tells the model to:

- act like a senior QA engineer
- generate only relevant test cases
- avoid duplicated or invented scenarios
- return a clean markdown table

### Groq Settings

In the `Groq` node:

- add your Groq API key
- model: `openai/gpt-oss-120b`
- temperature: `0.1`

If that Groq-hosted model is not available in your account, switch to another Groq chat model and keep the same flow.

### What to Test

- `Generate test cases for a login page with email, password, remember me, and sign in button.`
- `Generate test cases for password reset using email OTP verification.`
- `Generate test cases for a checkout page with coupon code, address, payment, and order confirmation.`

### What You Learn Here

- how to convert a prompt framework into a simple productized flow
- how LangFlow can be used for QA content generation, not only chat
- how to package a beginner workflow as an importable JSON

---

## Example 5: Very Simple QA Agent with Tools

This is the next step after prompt chains. An agent can decide when to use a tool.

### Goal

Build a QA helper agent that can answer testing questions and use a calculator for estimation or test execution math.

### Nodes to Add

- `Chat Input`
- `Groq`
- `Calculator`
- `Tool Calling Agent`
- `Chat Output`

### Connections

```text
Chat Input -> Tool Calling Agent
Groq (Language Model output) -> Tool Calling Agent
Calculator (Tool output) -> Tool Calling Agent
Tool Calling Agent -> Chat Output
```

Important:

- from `Groq`, use the `Language Model` output
- from `Calculator`, use the `Tool` output

### Groq Settings for Agent Use

In the `Groq` node:

- enable `Enable Tool Models`
- choose a tool-capable Groq model if required by your setup
- keep temperature low, usually `0` to `0.2`

### Agent Prompt

Inside `Tool Calling Agent`, use a simple system prompt such as:

```text
You are a QA assistant.
Help with software testing questions.
Use the calculator tool whenever the question needs arithmetic, estimation, capacity, or execution math.
Be concise and practical.
```

### What to Test

- `If one tester executes 25 test cases per day, how many tester-days are needed for 400 cases?`
- `We have 6 testers and 720 cases. Each tester executes 20 per day. How many days do we need?`
- `Give me a test execution estimate for 180 API cases if automation covers 60% and manual execution speed is 30/day.`

### What You Learn Here

- the difference between a chain and an agent
- how tools are attached to agents
- how LangFlow can support QA workflow automation, not just chat

---

## Example 6: Jira Story Score and HTML Report Agent

This flow fetches a Jira story, verifies its quality for QA readiness, scores it, and saves the result as an HTML report.

### Importable JSON

- [jira_story_score_html_agent_langflow.json](./jira_story_score_html_agent_langflow.json)

### Nodes to Add

- `API Request`
- `Parser`
- `Prompt Template`
- `Groq`
- `HTML Report Writer`
- `Chat Output`

### Connections

```text
API Request -> Parser -> Prompt Template -> Groq -> HTML Report Writer -> Chat Output
```

### What It Does

1. Fetches a Jira story through REST API.
2. Converts the raw payload into readable prompt input.
3. Scores the story using QA-focused criteria.
4. Generates a standalone HTML report.
5. Saves the report locally.

### Output

The report is saved by default at:

`Project_11_LangFlow/01_LangFlow_QuickStart/output/jira_story_score_report.html`

### Scoring Focus

The report scores the story on:

- clarity
- acceptance criteria quality
- testability
- business/context completeness
- dependency and risk clarity
- ambiguity reduction

### What You Learn Here

- how to turn Jira data into a QA quality gate
- how to generate local HTML artifacts from LangFlow
- how to build a useful reviewer-style agent instead of only a content generator

---

## Example 7: PDF to JSON Agent

This flow reads a PDF, extracts structured information, and saves it as JSON.

### Importable JSON

- [pdf_to_json_agent_langflow.json](./pdf_to_json_agent_langflow.json)

### Nodes to Add

- `Read File`
- `Groq`
- `Structured Output`
- `JSON Artifact Writer`
- `Chat Output`

### Connections

```text
Read File -> Structured Output
Groq (Language Model output) -> Structured Output
Structured Output -> JSON Artifact Writer -> Chat Output
```

### What It Does

1. Reads a PDF using LangFlow's file component.
2. Uses a language model to extract structured fields.
3. Produces JSON with title, summary, key entities, requirements, action items, and sections.
4. Saves that JSON locally.

### Setup Notes

- upload a PDF into the `Read File` node
- start with the default `Read File` setup and use the `Raw Content` path
- use a tool-capable Groq model for `Structured Output`

### Output

The JSON is saved by default at:

`Project_11_LangFlow/01_LangFlow_QuickStart/output/pdf_extraction.json`

### What You Learn Here

- how to turn unstructured PDFs into machine-readable data
- how to use `Structured Output` inside LangFlow
- how LangFlow can create data extraction pipelines, not only chat apps

---

## Now Move to Your First RAG Flow

After the seven examples above, RAG becomes much easier to understand.

RAG adds four new ideas:

1. `Load documents`
Bring PDFs, markdown, text, or CSV into the flow.

2. `Split documents`
Break long documents into smaller chunks.

3. `Embed and store`
Convert chunks into vectors and save them in a vector store.

4. `Retrieve before answering`
Fetch relevant context first, then generate the answer.

---

## Building Your First RAG Flow

### Step 1: Create a New Flow

- Click `New Flow`
- Choose `Blank Flow`
- Name it `QA Knowledge Base RAG`

### Step 2: Add Data Ingestion

- Add a `File` or `Directory` component
- Add `Recursive Character Text Splitter`
- Set:
  - `chunk_size = 1000`
  - `chunk_overlap = 200`

### Step 3: Add Embedding and Storage

- Add `OpenAI Embeddings`
- Add `Chroma`
- Connect:
  - splitter -> Chroma `ingest_data`
  - embeddings -> Chroma `embedding`

### Step 4: Add Question Answering

- Add `Chat Input`
- Add `Prompt Template`
- Add `OpenAI` or `Groq`
- Add `Chat Output`

Typical logical flow:

```text
Chat Input -> Retriever/Vector Store Search -> Prompt Template -> Model -> Chat Output
```

### Step 5: Test and Observe

- ask questions from your document set
- open execution trace
- inspect what chunks were retrieved
- improve chunk size, prompt, or retrieval settings

---

## LangFlow API Deployment

LangFlow can expose a flow through an API endpoint.

```python
import requests

LANGFLOW_API = "http://localhost:7860/api/v1/run/{flow_id}"

response = requests.post(
    LANGFLOW_API,
    json={
        "input_value": "What are the login test cases?",
        "output_type": "chat",
        "input_type": "chat",
    },
)

print(response.json())
```

---

## Practical Tips for Learners

1. Start with `Chat Input -> Model -> Chat Output` before adding more nodes.
2. Add only one new concept at a time: prompt, then tool, then retrieval.
3. Use execution traces heavily. They show exactly where the flow is going wrong.
4. Keep temperatures low while learning so behavior is easier to debug.
5. Export each working flow version before making it more complex.

---

## Suggested Learning Order

Follow this sequence inside Project 12:

1. This QuickStart
2. Simple Groq chatbot
3. Jira ticket review -> test plan + test cases
4. Prompt-based QA assistant
5. RICE-POT test case generator
6. Tool-based QA agent
7. Jira story score -> HTML report
8. PDF -> JSON agent
9. Naive RAG
10. Advanced RAG
11. Routing, Graph, Agentic, and Hybrid RAG patterns

---

**Next:** [Naive RAG Flow ->](../02_Naive_RAG_Flow/)
