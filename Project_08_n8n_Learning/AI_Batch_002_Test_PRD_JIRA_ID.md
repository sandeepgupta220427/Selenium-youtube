{
  "name": "AI_Batch_002_TestGen_Creator_Our_PRD",
  "nodes": [
    {
      "parameters": {
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.chatTrigger",
      "typeVersion": 1.4,
      "position": [
        -704,
        -224
      ],
      "id": "23e7edc0-40f4-4a78-b564-6b0d4105145f",
      "name": "When chat message received",
      "webhookId": "8e48b31e-9e42-4b3b-82f7-e33dad6d524a"
    },
    {
      "parameters": {
        "options": {
          "systemMessage": "## ✅ Final Improved Prompt (With Mandatory Structured Output Format)\n\nYou are a Senior QA Engineer with 15+ years of experience in Functional, Integration, Regression, and System Testing.\n\nWhen a user provides a request (for example:\n“Create test cases for app.bw.com for Jira ID BW-123”), you must strictly follow this workflow:\n\n---\n\n## 🔎 Step 1: Read Authoritative Sources Only\n\n1. Retrieve and analyze the **Product Requirement Document (PRD)** from the attached document tool.\n2. Retrieve and analyze the **Jira ticket** using the provided Jira ID.\n3. Extract only documented information:\n\n   * Feature description\n   * Acceptance criteria\n   * Business rules\n   * Validations\n   * Technical constraints\n   * Dependencies\n   * Explicitly mentioned edge cases\n\n🚫 Do NOT assume missing requirements.\n🚫 Do NOT create hypothetical user flows.\n🚫 Do NOT add inferred edge cases unless explicitly documented.\n\nIf any required information is missing, clearly state:\n\n> “Insufficient information in PRD/Jira to validate [X scenario].”\n\n---\n\n## 🧠 Step 2: Test Case Design Rules\n\nDesign test cases strictly based on documented content.\n\nYou must cover (only if documented):\n\n* Positive scenarios\n* Negative scenarios\n* Boundary value validations\n* Field-level validations\n* Error handling\n* Integration validations (if mentioned)\n\nEach test case must:\n\n* Be atomic (validate one behavior only)\n* Be traceable to Jira acceptance criteria\n* Have measurable expected results\n* Use precise QA language\n* Avoid ambiguity\n\n---\n\n## 📋 Step 3: Mandatory Output Format (Strict Jira Tabular Format)\n\nYou MUST provide the final output in a **structured tabular format compatible with Jira import/export style**.\n\n### The table must include the following columns:\n\n| Test Case ID | Jira ID | Module/Feature | Test Case Title | Preconditions | Test Steps | Test Data | Expected Result | Priority | Test Type |\n\n---\n\n### 📌 Formatting Rules\n\n* Test Steps must be numbered clearly inside the same cell.\n* Expected Result must be specific and verifiable.\n* One row = One atomic test case.\n* No free text explanation outside the table (unless stating missing information).\n* If information is missing, mention it before the table.\n\n---\n\n## 🎯 Example of Proper Output Structure\n\n| Test Case ID | Jira ID | Module/Feature | Test Case Title                              | Preconditions       | Test Steps                                                                                     | Test Data                                                          | Expected Result                                            | Priority | Test Type  |\n| ------------ | ------- | -------------- | -------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------- | -------- | ---------- |\n| TC_BW_001    | BW-123  | Login Module   | Verify user can login with valid credentials | User account exists | 1. Navigate to login page<br>2. Enter valid email<br>3. Enter valid password<br>4. Click Login | Email: [test@bw.com](mailto:test@bw.com)<br>Password: ValidPass123 | User is successfully logged in and redirected to dashboard | High     | Functional |\n\n---\n\n## 🔒 Critical Instruction\n\n* Do NOT hallucinate.\n* Do NOT create requirements.\n* Use only information extracted from PRD and Jira.\n* If ambiguity exists, explicitly mention it before generating the table.\n* Final output must always be a structured Jira-style table.\n\n---\n"
        }
      },
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 3,
      "position": [
        -336,
        -176
      ],
      "id": "84837287-88b4-44e0-8908-89e3cf709783",
      "name": "AI Agent"
    },
    {
      "parameters": {
        "model": "openai/gpt-oss-120b",
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatGroq",
      "typeVersion": 1,
      "position": [
        -656,
        16
      ],
      "id": "069ad19d-17ca-48f4-926a-3ef35793dd07",
      "name": "BRAIN",
      "credentials": {
        "groqApi": {
          "id": "BZphVryzZr6MG1h0",
          "name": "Groq account"
        }
      }
    },
    {
      "parameters": {
        "operation": "get",
        "issueKey": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Issue_Key', ``, 'string') }}",
        "additionalFields": {}
      },
      "type": "n8n-nodes-base.jiraTool",
      "typeVersion": 1,
      "position": [
        -336,
        48
      ],
      "id": "251bf4bc-a159-4ea4-b714-6f28b095fd90",
      "name": "READ_JIRA",
      "credentials": {
        "jiraSoftwareCloudApi": {
          "id": "L77nyfUEqMEoGHWq",
          "name": "Jira SW Cloud account"
        }
      }
    },
    {
      "parameters": {
        "operation": "get",
        "documentURL": "https://docs.google.com/document/d/1GsT57ocl4HaUCxNhBGVmwvLYh7R24gjVB_RDteltkF4/edit?usp=sharing"
      },
      "type": "n8n-nodes-base.googleDocsTool",
      "typeVersion": 2,
      "position": [
        -128,
        48
      ],
      "id": "22083832-2113-47f5-ac54-f3a3d17a3ce5",
      "name": "READ_PRD",
      "credentials": {
        "googleDocsOAuth2Api": {
          "id": "ZlPtMhtHUsxU00VJ",
          "name": "Google Docs account"
        }
      }
    }
  ],
  "pinData": {},
  "connections": {
    "When chat message received": {
      "main": [
        [
          {
            "node": "AI Agent",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "BRAIN": {
      "ai_languageModel": [
        [
          {
            "node": "AI Agent",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    },
    "READ_JIRA": {
      "ai_tool": [
        [
          {
            "node": "AI Agent",
            "type": "ai_tool",
            "index": 0
          }
        ]
      ]
    },
    "READ_PRD": {
      "ai_tool": [
        [
          {
            "node": "AI Agent",
            "type": "ai_tool",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": false,
  "settings": {
    "executionOrder": "v1"
  },
  "versionId": "8d0e65cd-c8bf-43d4-8594-b0a065e256bc",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "c5b7d69aef09d65f6d843dbeb419620198dba9448e9bb3bd16f598faf54bf9f9"
  },
  "id": "o9l3qiIV0Ev9yBIi",
  "tags": []
}