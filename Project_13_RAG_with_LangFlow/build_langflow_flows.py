import copy
import json
from pathlib import Path


ROOT = Path("/Users/promode/Documents/AITesterBlueprint/Project_13_RAG_with_LangFlow")
QUICKSTART_ROOT = Path("/Users/promode/Documents/AITesterBlueprint/Project_11_LangFlow")
REPO_ROOT = ROOT.parent
ADVANCED_FLOW = ROOT / "03_Advanced_RAG_Flow" / "advanced_rag_langflow_v6_fixed.json"
MODULAR_FLOW = ROOT / "04_Modular_RAG_Flow" / "modular_rag_langflow.json"
GRAPH_FLOW = ROOT / "05_Graph_RAG_Flow" / "graph_rag_langflow.json"
QUICKSTART_RICE_POT_FLOW = QUICKSTART_ROOT / "01_LangFlow_QuickStart" / "rice_pot_testcase_generator_langflow.json"
QUICKSTART_JIRA_FLOW = QUICKSTART_ROOT / "01_LangFlow_QuickStart" / "jira_ticket_testplan_langflow.json"
QUICKSTART_JIRA_SCORE_FLOW = QUICKSTART_ROOT / "01_LangFlow_QuickStart" / "jira_story_score_html_agent_langflow.json"
QUICKSTART_PDF_JSON_FLOW = QUICKSTART_ROOT / "01_LangFlow_QuickStart" / "pdf_to_json_agent_langflow.json"
GROQ_FLOW_TEMPLATE = REPO_ROOT / "Project_08_n8n_Learning" / "LF_RAG_TestCase_PDF_CSV_TC (2).json"
COMPONENT_INDEX = Path("/opt/anaconda3/lib/python3.12/site-packages/lfx/_assets/component_index.json")


MODULAR_CONTEXT_CODE = """from lfx.custom.custom_component.component import Component
from lfx.io import HandleInput, IntInput, Output
from lfx.schema.data import Data
from lfx.schema.message import Message


class ContextMergeFormatter(Component):
    display_name = "Context Merge Formatter"
    description = "Merge retriever outputs from multiple branches into one clean message context."
    icon = "combine"
    name = "ContextMergeFormatter"

    inputs = [
        HandleInput(
            name="input_data",
            display_name="Retriever Results",
            input_types=["Message", "Data", "DataFrame"],
            required=True,
            list=True,
        ),
        IntInput(
            name="max_chunks",
            display_name="Max Chunks",
            value=6,
            info="Maximum number of chunks to include in the merged context.",
        ),
    ]

    outputs = [
        Output(
            display_name="Message Output",
            name="message_output",
            method="build_message",
        ),
    ]

    def _flatten_items(self, value):
        if value is None:
            return []
        items = value if isinstance(value, list) else [value]
        flattened = []
        for item in items:
            if item is None:
                continue
            if isinstance(item, list):
                flattened.extend(self._flatten_items(item))
            elif hasattr(item, "to_data_list"):
                try:
                    flattened.extend(item.to_data_list())
                except Exception:  # noqa: BLE001
                    flattened.append(item)
            else:
                flattened.append(item)
        return flattened

    def _stringify_metadata(self, payload):
        for key in ("source", "path", "file_path", "title", "document_name", "filename", "collection_name"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _extract_text(self, item):
        if isinstance(item, Message):
            return (item.text or "").strip(), ""
        if isinstance(item, Data):
            payload = getattr(item, "data", {}) or {}
            text = (item.get_text() or "").strip()
            if not text:
                for key in ("text", "page_content", "content", "body", "chunk"):
                    value = payload.get(key)
                    if isinstance(value, str) and value.strip():
                        text = value.strip()
                        break
            if not text:
                text = "\\n".join(
                    f"{key}: {value}"
                    for key, value in payload.items()
                    if value is not None and str(value).strip() and key not in {"id"}
                ).strip()
            return text, self._stringify_metadata(payload)
        if isinstance(item, dict):
            text = ""
            for key in ("text", "page_content", "content", "body", "chunk"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    text = value.strip()
                    break
            if not text:
                text = "\\n".join(
                    f"{key}: {value}"
                    for key, value in item.items()
                    if value is not None and str(value).strip()
                ).strip()
            return text, self._stringify_metadata(item)
        text = str(item or "").strip()
        return text, ""

    def build_message(self) -> Message:
        items = self._flatten_items(self.input_data)
        chunks = []
        seen = set()
        limit = max(int(self.max_chunks or 6), 1)

        for item in items:
            text, label = self._extract_text(item)
            if not text:
                continue
            normalized = " ".join(text.split()).lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            if label:
                chunks.append(f"[{label}]\\n{text}")
            else:
                chunks.append(text)
            if len(chunks) >= limit:
                break

        if not chunks:
            message = Message(text="No retrieval context was returned by the selected branch.")
            self.status = message.text
            return message

        message = Message(text="\\n\\n---\\n\\n".join(chunks))
        self.status = message.text
        return message
"""


RICE_POT_TESTCASE_PROMPT = """Enhanced Prompt - Relevance-Strict Test Case Generator

R - Role
You are a senior QA engineer with 15 years of experience in web, API, and enterprise application testing.
You design practical, risk-focused test cases with strong coverage and minimal duplication.

I - Instructions
Generate a high-quality set of manual test cases for the feature or requirement below.
Focus only on scenarios that are directly relevant to the provided input.
Include positive, negative, boundary, validation, and usability checks where relevant.
Do not invent modules, workflows, or assumptions that are not implied by the input.
If information is missing, state concise assumptions first and then continue.

C - Context
Feature, user story, screen, or requirement:
{input}

E - Example
Expected output format:
| TC_ID | Scenario | Preconditions | Steps | Test Data | Expected Result | Priority | Type |
|---|---|---|---|---|---|---|---|
| TC_001 | Valid login | User account exists | 1. Open login page 2. Enter valid username and password 3. Click Login | valid credentials | User is logged in successfully | High | Positive |

P - Parameters
Keep the test cases precise, non-duplicative, and execution-friendly.
Prefer high-signal scenarios over generic filler.
Cover functional accuracy first, then validations and edge cases.

O - Output
Return only:
1. A short Assumptions section if needed.
2. A markdown table of test cases with the exact columns:
   TC_ID, Scenario, Preconditions, Steps, Test Data, Expected Result, Priority, Type

T - Tone
Technical, precise, QA-focused, and concise.
"""


JIRA_REVIEW_SYSTEM_MESSAGE = """You are a senior QA analyst reviewing a Jira ticket returned from the Jira REST API.

Convert the raw Jira payload into a clean test-analysis brief.
Return markdown with these headings exactly:
- Issue Key
- Summary
- Description
- Acceptance Criteria
- Priority
- Labels
- Dependencies
- Risks
- Open Questions

Rules:
- If the description or acceptance criteria are stored as Jira/Atlassian JSON, rewrite them into readable bullet points.
- If any field is missing, say `Not provided`.
- If the payload shows an API error, surface it clearly.
- Do not invent requirements or workflows.
"""


JIRA_PLAN_AND_CASES_PROMPT = """For this given input as user story:
{userStory}

Follow these instructions:

You are an expert QA lead specialized in Jira story analysis.
Create exactly two sections.

Section 1: Test Plan
Include:
- Objective
- Scope
- In Scope
- Out of Scope
- Assumptions
- Risks
- Test Types
- Test Environment
- Dependencies
- Entry Criteria
- Exit Criteria

Section 2: Test Cases
Return a markdown table with these exact columns:
| TC_ID | Scenario | Preconditions | Steps | Test Data | Expected Result | Priority | Type |

Rules:
- Use only the information present in the Jira review above.
- If information is missing, state it under Assumptions or Open Questions instead of inventing behavior.
- Keep test cases atomic and execution-ready.
- Cover positive, negative, validation, boundary, and integration scenarios only when justified by the Jira story.
- Keep the answer concise but complete.
"""


JIRA_STORY_SCORE_HTML_PROMPT = """Analyze the Jira story below and return ONLY standalone HTML5.

Jira story input:
{jira_story}

Task:
Review the Jira story for QA readiness and score it out of 100 using this rubric:
- Clarity of story goal: 20
- Acceptance criteria quality: 20
- Testability: 20
- Business/context completeness: 15
- Dependency and risk clarity: 10
- Ambiguity reduction / readiness for execution: 15

Requirements:
- Return only valid HTML with inline CSS. No markdown, no code fences, no explanations outside HTML.
- Show the total score prominently.
- Include a score breakdown table by category.
- Include sections for:
  - Jira issue summary
  - QA readiness verdict
  - Strengths
  - Gaps and ambiguities
  - Recommended improvements
  - Final QA recommendation
- If the Jira payload indicates an API error or missing content, produce an HTML error report instead.
- If any field is missing, show `Not provided`.
"""


PDF_TO_JSON_SYSTEM_PROMPT = """Extract structured JSON from the PDF text provided.

Rules:
- Use only the text present in the PDF extraction.
- Do not invent missing values.
- Preserve important sections, entities, risks, action items, and identifiers when present.
- If a field is not available, set it to null or an empty list/dict as appropriate.
- Return content that fits the provided schema only.
"""


HTML_REPORT_WRITER_CODE = """from pathlib import Path

from lfx.custom.custom_component.component import Component
from lfx.io import HandleInput, Output, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message


class HTMLReportWriter(Component):
    display_name = "HTML Report Writer"
    description = "Save an HTML report to a local file and return the saved path."
    icon = "file-text"
    name = "HTMLReportWriter"

    inputs = [
        HandleInput(
            name="report_html",
            display_name="HTML Report",
            input_types=["Message", "Data"],
            required=True,
        ),
        StrInput(
            name="file_path",
            display_name="File Path",
            value="/Users/promode/Documents/AITesterBlueprint/Project_11_LangFlow/01_LangFlow_QuickStart/output/jira_story_score_report.html",
            required=False,
            info="Absolute or relative path for the saved HTML report.",
        ),
    ]

    outputs = [
        Output(
            display_name="Saved Report",
            name="saved_report",
            method="save_report",
        ),
    ]

    def _coerce_text(self, value):
        if isinstance(value, Message):
            return str(value.text or "")
        if isinstance(value, Data):
            payload = getattr(value, "data", {}) or {}
            for key in ("html", "text", "report", "content", "message"):
                candidate = payload.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    return candidate
            return str(payload)
        return str(value or "")

    def save_report(self) -> Message:
        content = self._coerce_text(self.report_html).strip()
        if not content:
            raise ValueError("HTML report content is empty.")

        path = Path((self.file_path or "jira_story_score_report.html").strip()).expanduser()
        if not path.suffix:
            path = path.with_suffix(".html")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        preview = content[:500]
        if len(content) > 500:
            preview += "..."

        message = Message(
            text=f"HTML report saved to: {path}\\n\\nPreview:\\n{preview}"
        )
        self.status = message.text
        return message
"""


JSON_ARTIFACT_WRITER_CODE = """import json
from pathlib import Path

from lfx.custom.custom_component.component import Component
from lfx.io import HandleInput, Output, StrInput
from lfx.schema.data import Data
from lfx.schema.message import Message


class JSONArtifactWriter(Component):
    display_name = "JSON Artifact Writer"
    description = "Save structured data to a local JSON file and return the saved path."
    icon = "file-json"
    name = "JSONArtifactWriter"

    inputs = [
        HandleInput(
            name="input_data",
            display_name="Structured Data",
            input_types=["Data", "DataFrame", "Message"],
            required=True,
        ),
        StrInput(
            name="file_path",
            display_name="File Path",
            value="/Users/promode/Documents/AITesterBlueprint/Project_11_LangFlow/01_LangFlow_QuickStart/output/pdf_extraction.json",
            required=False,
            info="Absolute or relative path for the saved JSON file.",
        ),
    ]

    outputs = [
        Output(
            display_name="Saved JSON",
            name="saved_json",
            method="save_json",
        ),
    ]

    def _normalize(self, value):
        if isinstance(value, Data):
            return getattr(value, "data", {}) or {}
        if hasattr(value, "to_dict"):
            try:
                return value.to_dict(orient="records")
            except TypeError:
                try:
                    return value.to_dict()
                except Exception as exc:  # noqa: BLE001
                    raise ValueError(f"Unable to convert DataFrame-like input to dict: {exc}") from exc
        if isinstance(value, Message):
            text = str(value.text or "").strip()
            if not text:
                return {}
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"message": text}
        if isinstance(value, dict):
            return value
        return {"value": value}

    def save_json(self) -> Message:
        payload = self._normalize(self.input_data)
        path = Path((self.file_path or "pdf_extraction.json").strip()).expanduser()
        if not path.suffix:
            path = path.with_suffix(".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        preview = json.dumps(payload, indent=2, ensure_ascii=False)[:700]
        if len(preview) == 700:
            preview += "..."

        message = Message(text=f"JSON saved to: {path}\\n\\nPreview:\\n{preview}")
        self.status = message.text
        return message
"""


GRAPH_ENGINE_CODE = """import json
import re

from lfx.custom.custom_component.component import Component
from lfx.io import HandleInput, IntInput, MessageTextInput, Output
from lfx.schema.data import Data
from lfx.schema.message import Message


class GraphContextEngine(Component):
    display_name = "Graph Context Engine"
    description = "Build a lightweight knowledge graph from documents and retrieve graph facts for a question."
    icon = "git-branch"
    name = "GraphContextEngine"

    inputs = [
        HandleInput(
            name="documents",
            display_name="Documents",
            input_types=["Data", "DataFrame"],
            required=True,
            list=True,
        ),
        MessageTextInput(
            name="question",
            display_name="Question",
            input_types=["Message"],
            required=True,
        ),
        HandleInput(
            name="llm",
            display_name="Language Model",
            input_types=["LanguageModel"],
            required=True,
        ),
        IntInput(
            name="max_triplets_per_document",
            display_name="Max Triples Per Document",
            value=6,
        ),
        IntInput(
            name="top_k",
            display_name="Top Graph Facts",
            value=8,
        ),
    ]

    outputs = [
        Output(
            display_name="Context Message",
            name="context_message",
            method="build_context",
        ),
    ]

    def _llm_text(self, prompt: str) -> str:
        response = self.llm.invoke(prompt) if hasattr(self.llm, "invoke") else self.llm(prompt)
        if hasattr(response, "content"):
            return str(response.content or "")
        if hasattr(response, "text"):
            return str(response.text or "")
        return str(response or "")

    def _extract_json(self, raw: str):
        text = (raw or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        for candidate in (text,):
            try:
                return json.loads(candidate)
            except Exception:  # noqa: BLE001
                pass
        for pattern in (r"\\[.*\\]", r"\\{.*\\}"):
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                continue
            try:
                return json.loads(match.group(0))
            except Exception:  # noqa: BLE001
                continue
        return None

    def _normalize_documents(self, value):
        if value is None:
            return []
        items = value if isinstance(value, list) else [value]
        normalized = []
        for item in items:
            if item is None:
                continue
            if isinstance(item, Data):
                normalized.append(item)
            elif hasattr(item, "to_data_list"):
                try:
                    normalized.extend(item.to_data_list())
                except Exception:  # noqa: BLE001
                    continue
            elif isinstance(item, dict):
                normalized.append(Data(data=item))
        return normalized

    def _document_text(self, item: Data) -> str:
        text = (item.get_text() or "").strip()
        if text:
            return text
        payload = getattr(item, "data", {}) or {}
        for key in ("text", "page_content", "content", "body", "chunk"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return "\\n".join(
            f"{key}: {value}"
            for key, value in payload.items()
            if value is not None and str(value).strip()
        ).strip()

    def _clean_value(self, value) -> str:
        return re.sub(r"\\s+", " ", str(value or "")).strip()

    def _extract_triples(self, text: str):
        truncated = text[:4500]
        prompt = f'''
Extract up to {int(self.max_triplets_per_document or 6)} factual triples from the text below.
Return ONLY valid JSON as an array of objects in this exact format:
[
  {{"source": "...", "relation": "...", "target": "...", "evidence": "..."}}
]

Rules:
- Keep entities short and normalized.
- Keep relation names short and verb-like.
- Do not invent facts.
- Skip vague triples.

Text:
{truncated}
'''
        parsed = self._extract_json(self._llm_text(prompt))
        if isinstance(parsed, dict):
            parsed = parsed.get("triples", [])
        triples = []
        seen = set()
        for item in parsed or []:
            if not isinstance(item, dict):
                continue
            source = self._clean_value(item.get("source"))
            relation = self._clean_value(item.get("relation"))
            target = self._clean_value(item.get("target"))
            evidence = self._clean_value(item.get("evidence"))
            if not (source and relation and target):
                continue
            key = (source.lower(), relation.lower(), target.lower())
            if key in seen:
                continue
            seen.add(key)
            triples.append(
                {
                    "source": source,
                    "relation": relation,
                    "target": target,
                    "evidence": evidence,
                }
            )
        return triples

    def _question_signals(self, question: str):
        prompt = f'''
Extract the main entities and retrieval keywords from this question.
Return ONLY valid JSON in this format:
{{"entities": ["..."], "keywords": ["..."]}}

Question:
{question}
'''
        parsed = self._extract_json(self._llm_text(prompt))
        if isinstance(parsed, dict):
            entities = [self._clean_value(v) for v in parsed.get("entities", []) if self._clean_value(v)]
            keywords = [self._clean_value(v) for v in parsed.get("keywords", []) if self._clean_value(v)]
            if entities or keywords:
                return entities, keywords

        tokens = [token for token in re.findall(r"[A-Za-z0-9_]+", question.lower()) if len(token) > 2]
        return [], tokens[:8]

    def _score_triple(self, triple, entities, keywords):
        haystack = " ".join(
            [
                triple.get("source", ""),
                triple.get("relation", ""),
                triple.get("target", ""),
                triple.get("evidence", ""),
            ]
        ).lower()
        source_target = f'{triple.get("source", "")} {triple.get("target", "")}'.lower()
        score = 0
        for entity in entities:
            lowered = entity.lower()
            if lowered in source_target:
                score += 5
            elif lowered in haystack:
                score += 2
        for keyword in keywords:
            lowered = keyword.lower()
            if lowered in haystack:
                score += 1
        return score

    def build_context(self) -> Message:
        question = self._clean_value(self.question)
        docs = self._normalize_documents(self.documents)

        triples = []
        for doc in docs:
            text = self._document_text(doc)
            if text:
                triples.extend(self._extract_triples(text))

        if not triples:
            message = Message(text="No graph facts were extracted from the source documents.")
            self.status = message.text
            return message

        entities, keywords = self._question_signals(question)
        scored = [
            (self._score_triple(triple, entities, keywords), index, triple)
            for index, triple in enumerate(triples)
        ]
        scored.sort(key=lambda item: (item[0], -item[1]), reverse=True)

        limit = max(int(self.top_k or 8), 1)
        selected = [triple for score, _, triple in scored if score > 0][:limit]
        if not selected:
            selected = [triple for _, _, triple in scored[:limit]]

        lines = []
        for index, triple in enumerate(selected, start=1):
            evidence = triple.get("evidence", "")
            if evidence:
                lines.append(
                    f"[fact-{index}] {triple['source']} -[{triple['relation']}]-> {triple['target']} | evidence: {evidence}"
                )
            else:
                lines.append(f"[fact-{index}] {triple['source']} -[{triple['relation']}]-> {triple['target']}")

        header_parts = []
        if entities:
            header_parts.append("Question entities: " + ", ".join(entities))
        if keywords:
            header_parts.append("Question keywords: " + ", ".join(keywords))

        context = ""
        if header_parts:
            context += "\\n".join(header_parts) + "\\n\\n"
        context += "Graph facts:\\n" + "\\n".join(lines)

        message = Message(text=context)
        self.status = message.text
        return message
"""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_component(name: str) -> dict:
    component_index = load_json(COMPONENT_INDEX)
    for group_name, group in component_index["entries"]:
        component = group.get(name)
        if component:
            return copy.deepcopy(component)
    raise KeyError(f"Component {name} not found in component index")


def clone_node(nodes_by_id: dict, node_id: str, new_id: str, display_name: str, position: tuple[int, int]) -> dict:
    node = copy.deepcopy(nodes_by_id[node_id])
    node["id"] = new_id
    node["data"]["id"] = new_id
    node["data"]["node"]["display_name"] = display_name
    node["position"] = {"x": position[0], "y": position[1]}
    node["selected"] = False
    node["dragging"] = False
    return node


def build_component_node(
    *,
    component_name: str,
    node_id: str,
    position: tuple[int, int],
    flow_id: str,
    display_name: str | None = None,
    data_type: str | None = None,
    measured: tuple[int, int] = (320, 320),
    show_node: bool = True,
    selected_output: str | None = None,
) -> dict:
    component = load_component(component_name)
    component.setdefault("custom_fields", {})
    component["lf_version"] = "1.7.2"
    component["template"].setdefault("_frontend_node_flow_id", {"value": flow_id})
    if display_name:
        component["display_name"] = display_name
    if not component.get("name"):
        component["name"] = component_name.replace(" ", "")

    node = {
        "data": {
            "id": node_id,
            "node": component,
            "showNode": show_node,
            "type": data_type or component_name,
        },
        "dragging": False,
        "id": node_id,
        "measured": {"height": measured[1], "width": measured[0]},
        "position": {"x": position[0], "y": position[1]},
        "selected": False,
        "type": "genericNode",
    }

    if selected_output is None and len(component.get("outputs", [])) == 1:
        selected_output = component["outputs"][0]["name"]
    if selected_output:
        node["data"]["selected_output"] = selected_output
    return normalize_flow_node(node, flow_id)


def normalize_flow_node(node: dict, flow_id: str, lf_version: str = "1.7.2") -> dict:
    template = node["data"]["node"].get("template", {})
    if "_frontend_node_flow_id" in template:
        template["_frontend_node_flow_id"]["value"] = flow_id
    template.pop("_frontend_node_folder_id", None)
    node["data"]["node"]["lf_version"] = lf_version
    return node


def edge_handle_repr(kind: str, payload: dict) -> str:
    if kind == "source":
        output_types = ",".join(f"œ{item}œ" for item in payload["output_types"])
        return (
            f"{{œdataTypeœ:œ{payload['dataType']}œ,œidœ:œ{payload['id']}œ,"
            f"œnameœ:œ{payload['name']}œ,œoutput_typesœ:[{output_types}]}}"
        )
    input_types = ",".join(f"œ{item}œ" for item in payload["inputTypes"])
    return (
        f"{{œfieldNameœ:œ{payload['fieldName']}œ,œidœ:œ{payload['id']}œ,"
        f"œinputTypesœ:[{input_types}],œtypeœ:œ{payload['type']}œ}}"
    )


def make_edge(
    source_id: str,
    source_type: str,
    source_name: str,
    source_output_types: list[str],
    target_id: str,
    target_field: str,
    target_input_types: list[str],
    target_type: str,
) -> dict:
    source_payload = {
        "dataType": source_type,
        "id": source_id,
        "name": source_name,
        "output_types": source_output_types,
    }
    target_payload = {
        "fieldName": target_field,
        "id": target_id,
        "inputTypes": target_input_types,
        "type": target_type,
    }
    source_handle = edge_handle_repr("source", source_payload)
    target_handle = edge_handle_repr("target", target_payload)
    return {
        "animated": False,
        "className": "",
        "data": {
            "sourceHandle": source_payload,
            "targetHandle": target_payload,
        },
        "id": f"xy-edge__{source_id}{source_handle}-{target_id}{target_handle}",
        "selected": False,
        "source": source_id,
        "sourceHandle": source_handle,
        "target": target_id,
        "targetHandle": target_handle,
    }


def build_custom_component_node(
    *,
    node_id: str,
    display_name: str,
    description: str,
    name: str,
    code: str,
    field_order: list[str],
    outputs: list[dict],
    template: dict,
    position: tuple[int, int],
    measured: tuple[int, int] = (320, 260),
    base_classes: list[str] | None = None,
) -> dict:
    component = load_component("CustomComponent")
    component["display_name"] = display_name
    component["description"] = description
    component["edited"] = True
    component["field_order"] = field_order
    component["lf_version"] = "1.7.2"
    component["outputs"] = outputs
    component["template"] = {"_type": "Component", "code": component["template"]["code"], **template}
    component["template"]["code"]["value"] = code
    component["base_classes"] = base_classes or ["Message"]
    component["metadata"]["module"] = "lfx.components.custom_component.custom_component.CustomComponent"
    component["name"] = name

    return {
        "data": {
            "id": node_id,
            "node": component,
            "showNode": True,
            "type": "CustomComponent",
        },
        "dragging": False,
        "id": node_id,
        "measured": {"height": measured[1], "width": measured[0]},
        "position": {"x": position[0], "y": position[1]},
        "selected": False,
        "type": "genericNode",
    }


def replace_node(nodes: list[dict], new_node: dict) -> None:
    for index, node in enumerate(nodes):
        if node["id"] == new_node["id"]:
            nodes[index] = new_node
            return
    raise KeyError(f"Node {new_node['id']} not found")


def build_modular_flow() -> dict:
    modular = load_json(MODULAR_FLOW)
    context_node = build_custom_component_node(
        node_id="TypeConverter-Context-MOD1",
        display_name="Context Merge Formatter",
        description="Merge retriever results from the routed branches into a single prompt-ready message.",
        name="ContextMergeFormatter",
        code=MODULAR_CONTEXT_CODE,
        field_order=["input_data", "max_chunks"],
        outputs=[
            {
                "allows_loop": False,
                "cache": True,
                "display_name": "Message Output",
                "group_outputs": False,
                "method": "build_message",
                "name": "message_output",
                "selected": "Message",
                "tool_mode": True,
                "types": ["Message"],
                "value": "__UNDEFINED__",
            }
        ],
        template={
            "input_data": {
                "_input_type": "HandleInput",
                "advanced": False,
                "display_name": "Retriever Results",
                "dynamic": False,
                "info": "",
                "input_types": ["Message", "Data", "DataFrame"],
                "list": True,
                "list_add_label": "Add More",
                "name": "input_data",
                "override_skip": False,
                "placeholder": "",
                "required": True,
                "show": True,
                "title_case": False,
                "trace_as_metadata": True,
                "track_in_telemetry": False,
                "type": "other",
                "value": "",
            },
            "max_chunks": {
                "_input_type": "IntInput",
                "advanced": False,
                "display_name": "Max Chunks",
                "dynamic": False,
                "info": "Maximum number of chunks to include in the merged context.",
                "list": False,
                "list_add_label": "Add More",
                "name": "max_chunks",
                "override_skip": False,
                "placeholder": "",
                "required": False,
                "show": True,
                "title_case": False,
                "tool_mode": False,
                "trace_as_metadata": True,
                "track_in_telemetry": True,
                "type": "int",
                "value": 6,
            },
        },
        position=(1360, 270),
        base_classes=["Message"],
    )
    replace_node(modular["data"]["nodes"], context_node)

    for index, edge in enumerate(modular["data"]["edges"]):
        if edge["source"] == "TypeConverter-Context-MOD1" and edge["target"] == "Prompt Template-MOD1":
            modular["data"]["edges"][index] = make_edge(
                "TypeConverter-Context-MOD1",
                "CustomComponent",
                "message_output",
                ["Message"],
                "Prompt Template-MOD1",
                "context",
                ["Message"],
                "str",
            )
            break

    modular["description"] = (
        "Modular RAG with Smart Router, three Chroma branches, and a custom context merger for routed retrieval."
    )
    modular["tags"] = ["rag", "modular", "router", "langflow", "smart-router"]
    return modular


def build_rice_pot_quickstart_flow() -> dict:
    starter = load_json(GROQ_FLOW_TEMPLATE)
    nodes_by_id = {node["id"]: node for node in starter["data"]["nodes"]}
    flow_id = "rice-pot-testcase-generator"

    chat_input = clone_node(nodes_by_id, "ChatInput-pYbLS", "ChatInput-RICE1", "Chat Input", (80, 300))
    prompt = clone_node(
        nodes_by_id,
        "Prompt Template-f1od3",
        "Prompt Template-RICE1",
        "RICE-POT Prompt Template",
        (430, 130),
    )
    groq = clone_node(nodes_by_id, "GroqModel-l0aVj", "GroqModel-RICE1", "Groq", (900, 170))
    chat_output = clone_node(nodes_by_id, "ChatOutput-7VAtB", "ChatOutput-RICE1", "Chat Output", (1360, 300))

    for node in (chat_input, prompt, groq, chat_output):
        normalize_flow_node(node, flow_id)

    prompt["data"]["node"]["custom_fields"]["template"] = ["input"]
    prompt["data"]["node"]["template"]["template"]["value"] = RICE_POT_TESTCASE_PROMPT

    groq_template = groq["data"]["node"]["template"]
    model_name = "openai/gpt-oss-120b"
    if model_name not in groq_template["model_name"]["options"]:
        groq_template["model_name"]["options"].append(model_name)
    groq_template["model_name"]["value"] = model_name
    groq_template["temperature"]["value"] = 0.1
    groq_template["system_message"]["value"] = ""
    groq_template["stream"]["value"] = False
    groq_template["tool_model_enabled"]["value"] = False

    nodes = [chat_input, prompt, groq, chat_output]
    edges = [
        make_edge(
            "ChatInput-RICE1",
            "ChatInput",
            "message",
            ["Message"],
            "Prompt Template-RICE1",
            "input",
            ["Message"],
            "str",
        ),
        make_edge(
            "Prompt Template-RICE1",
            "Prompt Template",
            "prompt",
            ["Message"],
            "GroqModel-RICE1",
            "input_value",
            ["Message"],
            "str",
        ),
        make_edge(
            "GroqModel-RICE1",
            "GroqModel",
            "text_output",
            ["Message"],
            "ChatOutput-RICE1",
            "input_value",
            ["Data", "DataFrame", "Message"],
            "other",
        ),
    ]

    return {
        "data": {
            "edges": edges,
            "nodes": nodes,
            "viewport": {"x": 124.0, "y": 22.0, "zoom": 0.82},
        },
        "description": "QuickStart Langflow flow for generating test cases with a RICE-POT prompt and Groq.",
        "endpoint_name": flow_id,
        "id": flow_id,
        "is_component": False,
        "last_tested_version": "1.7.2",
        "name": "RICE-POT Test Case Generator",
        "tags": ["quickstart", "langflow", "groq", "test-cases", "rice-pot"],
    }


def build_jira_ticket_testplan_flow() -> dict:
    starter = load_json(GROQ_FLOW_TEMPLATE)
    nodes_by_id = {node["id"]: node for node in starter["data"]["nodes"]}
    flow_id = "jira-ticket-testplan-generator"

    api_request = build_component_node(
        component_name="APIRequest",
        node_id="APIRequest-JIRA1",
        position=(60, 240),
        flow_id=flow_id,
        display_name="Fetch Jira Ticket",
        data_type="APIRequest",
        measured=(340, 520),
    )
    api_request_template = api_request["data"]["node"]["template"]
    api_request_template["mode"]["value"] = "URL"
    api_request_template["method"]["value"] = "GET"
    api_request_template["url_input"]["value"] = "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123"
    api_request_template["headers"]["value"] = [
        {"key": "Accept", "value": "application/json"},
        {"key": "Authorization", "value": "Basic <base64_email_colon_api_token>"},
        {"key": "User-Agent", "value": "Langflow/1.0"},
    ]
    api_request_template["timeout"]["value"] = 30
    api_request_template["follow_redirects"]["value"] = False
    api_request_template["include_httpx_metadata"]["value"] = False
    api_request_template["save_to_file"]["value"] = False

    parser = build_component_node(
        component_name="ParserComponent",
        node_id="Parser-JIRA1",
        position=(430, 270),
        flow_id=flow_id,
        display_name="Jira Payload Parser",
        data_type="ParserComponent",
        measured=(320, 330),
    )
    parser_template = parser["data"]["node"]["template"]
    parser_template["mode"]["value"] = "Parser"
    parser_template["pattern"]["value"] = (
        "Jira API Source: {source}\n"
        "HTTP Status: {status_code}\n"
        "API Error: {error}\n\n"
        "Jira Ticket Payload:\n{result}"
    )
    parser_template["sep"]["value"] = "\n"

    review_llm = clone_node(nodes_by_id, "GroqModel-l0aVj", "GroqModel-REVIEW-JIRA1", "Jira Review LLM", (810, 230))
    final_prompt = clone_node(
        nodes_by_id,
        "Prompt Template-f1od3",
        "Prompt Template-JIRA1",
        "Plan + Test Cases Prompt",
        (1220, 140),
    )
    final_llm = clone_node(
        nodes_by_id,
        "GroqModel-l0aVj",
        "GroqModel-GEN-JIRA1",
        "Test Plan + Cases LLM",
        (1630, 220),
    )
    chat_output = clone_node(nodes_by_id, "ChatOutput-7VAtB", "ChatOutput-JIRA1", "Chat Output", (2070, 320))

    for node in (review_llm, final_prompt, final_llm, chat_output):
        normalize_flow_node(node, flow_id)

    review_template = review_llm["data"]["node"]["template"]
    review_template["system_message"]["value"] = JIRA_REVIEW_SYSTEM_MESSAGE
    review_template["model_name"]["value"] = "llama-3.3-70b-versatile"
    review_template["temperature"]["value"] = 0
    review_template["stream"]["value"] = False
    review_template["tool_model_enabled"]["value"] = False

    final_prompt["data"]["node"]["custom_fields"]["template"] = ["userStory"]
    final_prompt["data"]["node"]["template"]["template"]["value"] = JIRA_PLAN_AND_CASES_PROMPT

    final_template = final_llm["data"]["node"]["template"]
    final_template["system_message"]["value"] = ""
    final_template["model_name"]["value"] = "llama-3.3-70b-versatile"
    final_template["temperature"]["value"] = 0.1
    final_template["stream"]["value"] = False
    final_template["tool_model_enabled"]["value"] = False

    nodes = [api_request, parser, review_llm, final_prompt, final_llm, chat_output]
    edges = [
        make_edge(
            "APIRequest-JIRA1",
            "APIRequest",
            "data",
            ["Data"],
            "Parser-JIRA1",
            "input_data",
            ["DataFrame", "Data"],
            "other",
        ),
        make_edge(
            "Parser-JIRA1",
            "ParserComponent",
            "parsed_text",
            ["Message"],
            "GroqModel-REVIEW-JIRA1",
            "input_value",
            ["Message"],
            "str",
        ),
        make_edge(
            "GroqModel-REVIEW-JIRA1",
            "GroqModel",
            "text_output",
            ["Message"],
            "Prompt Template-JIRA1",
            "userStory",
            ["Message"],
            "str",
        ),
        make_edge(
            "Prompt Template-JIRA1",
            "Prompt Template",
            "prompt",
            ["Message"],
            "GroqModel-GEN-JIRA1",
            "input_value",
            ["Message"],
            "str",
        ),
        make_edge(
            "GroqModel-GEN-JIRA1",
            "GroqModel",
            "text_output",
            ["Message"],
            "ChatOutput-JIRA1",
            "input_value",
            ["Data", "DataFrame", "Message"],
            "other",
        ),
    ]

    return {
        "data": {
            "edges": edges,
            "nodes": nodes,
            "viewport": {"x": 163.0, "y": 109.0, "zoom": 0.69},
        },
        "description": "QuickStart Langflow flow that fetches a Jira ticket, reviews it, and generates a test plan plus test cases.",
        "endpoint_name": flow_id,
        "id": flow_id,
        "is_component": False,
        "last_tested_version": "1.7.2",
        "name": "Jira Ticket Review -> Test Plan + Test Cases",
        "tags": ["quickstart", "langflow", "jira", "test-plan", "test-cases", "groq"],
    }


def build_jira_story_score_flow() -> dict:
    starter = load_json(GROQ_FLOW_TEMPLATE)
    nodes_by_id = {node["id"]: node for node in starter["data"]["nodes"]}
    flow_id = "jira-story-score-html-agent"

    api_request = build_component_node(
        component_name="APIRequest",
        node_id="APIRequest-SCORE1",
        position=(60, 250),
        flow_id=flow_id,
        display_name="Fetch Jira Story",
        data_type="APIRequest",
        measured=(340, 520),
    )
    api_template = api_request["data"]["node"]["template"]
    api_template["mode"]["value"] = "URL"
    api_template["method"]["value"] = "GET"
    api_template["url_input"]["value"] = "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123"
    api_template["headers"]["value"] = [
        {"key": "Accept", "value": "application/json"},
        {"key": "Authorization", "value": "Basic <base64_email_colon_api_token>"},
        {"key": "User-Agent", "value": "Langflow/1.0"},
    ]
    api_template["timeout"]["value"] = 30

    parser = build_component_node(
        component_name="ParserComponent",
        node_id="Parser-SCORE1",
        position=(430, 280),
        flow_id=flow_id,
        display_name="Story Payload Parser",
        data_type="ParserComponent",
        measured=(320, 330),
    )
    parser_template = parser["data"]["node"]["template"]
    parser_template["mode"]["value"] = "Parser"
    parser_template["pattern"]["value"] = (
        "Jira API Source: {source}\n"
        "HTTP Status: {status_code}\n"
        "API Error: {error}\n\n"
        "Jira Story Payload:\n{result}"
    )

    prompt = clone_node(
        nodes_by_id,
        "Prompt Template-f1od3",
        "Prompt Template-SCORE1",
        "Story Score HTML Prompt",
        (810, 180),
    )
    groq = clone_node(nodes_by_id, "GroqModel-l0aVj", "GroqModel-SCORE1", "Story Score LLM", (1220, 220))
    html_writer = build_custom_component_node(
        node_id="CustomComponent-SCORE1",
        display_name="HTML Report Writer",
        description="Save the generated HTML report to a local file.",
        name="HTMLReportWriter",
        code=HTML_REPORT_WRITER_CODE,
        field_order=["report_html", "file_path"],
        outputs=[
            {
                "allows_loop": False,
                "cache": True,
                "display_name": "Saved Report",
                "group_outputs": False,
                "method": "save_report",
                "name": "saved_report",
                "selected": "Message",
                "tool_mode": True,
                "types": ["Message"],
                "value": "__UNDEFINED__",
            }
        ],
        template={
            "report_html": {
                "_input_type": "HandleInput",
                "advanced": False,
                "display_name": "HTML Report",
                "dynamic": False,
                "info": "",
                "input_types": ["Message", "Data"],
                "list": False,
                "list_add_label": "Add More",
                "name": "report_html",
                "override_skip": False,
                "placeholder": "",
                "required": True,
                "show": True,
                "title_case": False,
                "trace_as_metadata": True,
                "track_in_telemetry": False,
                "type": "other",
                "value": "",
            },
            "file_path": {
                "_input_type": "StrInput",
                "advanced": False,
                "display_name": "File Path",
                "dynamic": False,
                "info": "Absolute or relative path for the saved HTML report.",
                "name": "file_path",
                "override_skip": False,
                "placeholder": "",
                "required": False,
                "show": True,
                "title_case": False,
                "tool_mode": False,
                "trace_as_metadata": True,
                "track_in_telemetry": True,
                "type": "str",
                "value": str(
                    QUICKSTART_ROOT
                    / "01_LangFlow_QuickStart"
                    / "output"
                    / "jira_story_score_report.html"
                ),
            },
        },
        position=(1650, 250),
        measured=(360, 250),
        base_classes=["Message"],
    )
    chat_output = clone_node(nodes_by_id, "ChatOutput-7VAtB", "ChatOutput-SCORE1", "Chat Output", (2060, 320))

    for node in (prompt, groq, chat_output):
        normalize_flow_node(node, flow_id)

    prompt["data"]["node"]["custom_fields"]["template"] = ["jira_story"]
    prompt["data"]["node"]["template"]["template"]["value"] = JIRA_STORY_SCORE_HTML_PROMPT

    groq_template = groq["data"]["node"]["template"]
    groq_template["system_message"]["value"] = ""
    groq_template["model_name"]["value"] = "llama-3.3-70b-versatile"
    groq_template["temperature"]["value"] = 0
    groq_template["stream"]["value"] = False
    groq_template["tool_model_enabled"]["value"] = False

    nodes = [api_request, parser, prompt, groq, html_writer, chat_output]
    edges = [
        make_edge(
            "APIRequest-SCORE1",
            "APIRequest",
            "data",
            ["Data"],
            "Parser-SCORE1",
            "input_data",
            ["DataFrame", "Data"],
            "other",
        ),
        make_edge(
            "Parser-SCORE1",
            "ParserComponent",
            "parsed_text",
            ["Message"],
            "Prompt Template-SCORE1",
            "jira_story",
            ["Message"],
            "str",
        ),
        make_edge(
            "Prompt Template-SCORE1",
            "Prompt Template",
            "prompt",
            ["Message"],
            "GroqModel-SCORE1",
            "input_value",
            ["Message"],
            "str",
        ),
        make_edge(
            "GroqModel-SCORE1",
            "GroqModel",
            "text_output",
            ["Message"],
            "CustomComponent-SCORE1",
            "report_html",
            ["Message", "Data"],
            "other",
        ),
        make_edge(
            "CustomComponent-SCORE1",
            "CustomComponent",
            "saved_report",
            ["Message"],
            "ChatOutput-SCORE1",
            "input_value",
            ["Data", "DataFrame", "Message"],
            "other",
        ),
    ]

    return {
        "data": {
            "edges": edges,
            "nodes": nodes,
            "viewport": {"x": 126.0, "y": 90.0, "zoom": 0.67},
        },
        "description": "QuickStart Langflow flow that fetches a Jira story, scores QA readiness, and saves an HTML report.",
        "endpoint_name": flow_id,
        "id": flow_id,
        "is_component": False,
        "last_tested_version": "1.7.2",
        "name": "Jira Story Score HTML Agent",
        "tags": ["quickstart", "langflow", "jira", "html", "score", "qa"],
    }


def build_pdf_to_json_flow() -> dict:
    starter = load_json(GROQ_FLOW_TEMPLATE)
    nodes_by_id = {node["id"]: node for node in starter["data"]["nodes"]}
    flow_id = "pdf-to-json-agent"

    read_file = build_component_node(
        component_name="File",
        node_id="File-PDF1",
        position=(80, 260),
        flow_id=flow_id,
        display_name="Read PDF",
        data_type="File",
        measured=(360, 520),
        selected_output="message",
    )
    file_template = read_file["data"]["node"]["template"]
    file_template["advanced_mode"]["value"] = False
    file_template["pipeline"]["value"] = "standard"
    file_template["ocr_engine"]["value"] = "easyocr"
    file_template["markdown"]["value"] = False
    file_template["separator"]["value"] = "\n\n"
    file_template["delete_server_file_after_processing"]["value"] = False
    file_template["ignore_unsupported_extensions"]["value"] = True

    groq = clone_node(nodes_by_id, "GroqModel-l0aVj", "GroqModel-PDF1", "Structured Extraction LLM", (510, 300))
    normalize_flow_node(groq, flow_id)
    groq_template = groq["data"]["node"]["template"]
    groq_template["system_message"]["value"] = ""
    groq_template["model_name"]["value"] = "llama-3.3-70b-versatile"
    groq_template["temperature"]["value"] = 0
    groq_template["stream"]["value"] = False
    groq_template["tool_model_enabled"]["value"] = True

    structured = build_component_node(
        component_name="StructuredOutput",
        node_id="StructuredOutput-PDF1",
        position=(930, 170),
        flow_id=flow_id,
        display_name="PDF Structured Output",
        data_type="StructuredOutput",
        measured=(360, 420),
        selected_output="structured_output",
    )
    structured_template = structured["data"]["node"]["template"]
    structured_template["schema_name"]["value"] = "PDFExtraction"
    structured_template["system_prompt"]["value"] = PDF_TO_JSON_SYSTEM_PROMPT
    structured_template["output_schema"]["value"] = [
        {
            "name": "document_title",
            "description": "Best available title of the PDF document.",
            "type": "str",
            "multiple": "False",
        },
        {
            "name": "document_type",
            "description": "Document class such as PRD, test plan, invoice, article, or manual.",
            "type": "str",
            "multiple": "False",
        },
        {
            "name": "summary",
            "description": "Concise summary of the full document.",
            "type": "str",
            "multiple": "False",
        },
        {
            "name": "key_entities",
            "description": "Important systems, product names, teams, people, or entities mentioned.",
            "type": "str",
            "multiple": "True",
        },
        {
            "name": "key_requirements",
            "description": "Core requirements, decisions, or obligations found in the document.",
            "type": "str",
            "multiple": "True",
        },
        {
            "name": "action_items",
            "description": "Explicit next steps or action items.",
            "type": "str",
            "multiple": "True",
        },
        {
            "name": "dates_and_identifiers",
            "description": "Dictionary of important dates, versions, IDs, or references.",
            "type": "dict",
            "multiple": "False",
        },
        {
            "name": "sections",
            "description": "Dictionary of major sections and their extracted content summaries.",
            "type": "dict",
            "multiple": "False",
        },
    ]

    json_writer = build_custom_component_node(
        node_id="CustomComponent-PDF1",
        display_name="JSON Artifact Writer",
        description="Save structured extraction output to a local JSON file.",
        name="JSONArtifactWriter",
        code=JSON_ARTIFACT_WRITER_CODE,
        field_order=["input_data", "file_path"],
        outputs=[
            {
                "allows_loop": False,
                "cache": True,
                "display_name": "Saved JSON",
                "group_outputs": False,
                "method": "save_json",
                "name": "saved_json",
                "selected": "Message",
                "tool_mode": True,
                "types": ["Message"],
                "value": "__UNDEFINED__",
            }
        ],
        template={
            "input_data": {
                "_input_type": "HandleInput",
                "advanced": False,
                "display_name": "Structured Data",
                "dynamic": False,
                "info": "",
                "input_types": ["Data", "DataFrame", "Message"],
                "list": False,
                "list_add_label": "Add More",
                "name": "input_data",
                "override_skip": False,
                "placeholder": "",
                "required": True,
                "show": True,
                "title_case": False,
                "trace_as_metadata": True,
                "track_in_telemetry": False,
                "type": "other",
                "value": "",
            },
            "file_path": {
                "_input_type": "StrInput",
                "advanced": False,
                "display_name": "File Path",
                "dynamic": False,
                "info": "Absolute or relative path for the saved JSON file.",
                "name": "file_path",
                "override_skip": False,
                "placeholder": "",
                "required": False,
                "show": True,
                "title_case": False,
                "tool_mode": False,
                "trace_as_metadata": True,
                "track_in_telemetry": True,
                "type": "str",
                "value": str(
                    QUICKSTART_ROOT
                    / "01_LangFlow_QuickStart"
                    / "output"
                    / "pdf_extraction.json"
                ),
            },
        },
        position=(1350, 260),
        measured=(360, 250),
        base_classes=["Message"],
    )
    chat_output = clone_node(nodes_by_id, "ChatOutput-7VAtB", "ChatOutput-PDF1", "Chat Output", (1760, 330))
    normalize_flow_node(chat_output, flow_id)

    nodes = [read_file, groq, structured, json_writer, chat_output]
    edges = [
        make_edge(
            "File-PDF1",
            "File",
            "message",
            ["Message"],
            "StructuredOutput-PDF1",
            "input_value",
            ["Message"],
            "str",
        ),
        make_edge(
            "GroqModel-PDF1",
            "GroqModel",
            "model_output",
            ["LanguageModel"],
            "StructuredOutput-PDF1",
            "llm",
            ["LanguageModel"],
            "other",
        ),
        make_edge(
            "StructuredOutput-PDF1",
            "StructuredOutput",
            "structured_output",
            ["Data"],
            "CustomComponent-PDF1",
            "input_data",
            ["Data", "DataFrame", "Message"],
            "other",
        ),
        make_edge(
            "CustomComponent-PDF1",
            "CustomComponent",
            "saved_json",
            ["Message"],
            "ChatOutput-PDF1",
            "input_value",
            ["Data", "DataFrame", "Message"],
            "other",
        ),
    ]

    return {
        "data": {
            "edges": edges,
            "nodes": nodes,
            "viewport": {"x": 132.0, "y": 114.0, "zoom": 0.73},
        },
        "description": "QuickStart Langflow flow that reads a PDF, extracts structured JSON, and saves the output locally.",
        "endpoint_name": flow_id,
        "id": flow_id,
        "is_component": False,
        "last_tested_version": "1.7.2",
        "name": "PDF to JSON Agent",
        "tags": ["quickstart", "langflow", "pdf", "json", "structured-output"],
    }


def build_graph_flow() -> dict:
    advanced = load_json(ADVANCED_FLOW)
    nodes_by_id = {node["id"]: node for node in advanced["data"]["nodes"]}

    directory = clone_node(nodes_by_id, "Directory-WyRy4", "Directory-GRAPH1", "Graph Source Docs", (80, 120))
    directory["data"]["node"]["template"]["path"]["value"] = (
        "/Users/promode/Documents/AITesterBlueprint/Project_12_RAG_Basics/RAG_Documents"
    )
    directory["data"]["node"]["template"]["types"]["value"] = ["pdf", "txt", "md", "csv"]

    graph_llm = clone_node(nodes_by_id, "OpenAIModel-QqXOx", "OpenAIModel-GRAPH1", "Graph Builder LLM", (380, 120))
    graph_llm["data"]["node"]["template"]["model_name"]["value"] = "gpt-4o-mini"
    graph_llm["data"]["node"]["template"]["temperature"]["value"] = 0

    chat_input = clone_node(nodes_by_id, "ChatInput-oiS9v", "ChatInput-GRAPH1", "Chat Input", (80, 520))

    graph_engine = build_custom_component_node(
        node_id="CustomComponent-GRAPH1",
        display_name="Graph Context Engine",
        description="Extract graph triples from documents and return graph-based context for a question.",
        name="GraphContextEngine",
        code=GRAPH_ENGINE_CODE,
        field_order=["documents", "question", "llm", "max_triplets_per_document", "top_k"],
        outputs=[
            {
                "allows_loop": False,
                "cache": True,
                "display_name": "Context Message",
                "group_outputs": False,
                "method": "build_context",
                "name": "context_message",
                "selected": "Message",
                "tool_mode": True,
                "types": ["Message"],
                "value": "__UNDEFINED__",
            }
        ],
        template={
            "documents": {
                "_input_type": "HandleInput",
                "advanced": False,
                "display_name": "Documents",
                "dynamic": False,
                "info": "",
                "input_types": ["Data", "DataFrame"],
                "list": True,
                "list_add_label": "Add More",
                "name": "documents",
                "override_skip": False,
                "placeholder": "",
                "required": True,
                "show": True,
                "title_case": False,
                "trace_as_metadata": True,
                "track_in_telemetry": False,
                "type": "other",
                "value": "",
            },
            "question": {
                "_input_type": "MessageTextInput",
                "advanced": False,
                "display_name": "Question",
                "dynamic": False,
                "info": "",
                "input_types": ["Message"],
                "list": False,
                "list_add_label": "Add More",
                "load_from_db": False,
                "name": "question",
                "override_skip": False,
                "placeholder": "",
                "required": True,
                "show": True,
                "title_case": False,
                "tool_mode": False,
                "trace_as_input": True,
                "trace_as_metadata": True,
                "track_in_telemetry": False,
                "type": "str",
                "value": "",
            },
            "llm": {
                "_input_type": "HandleInput",
                "advanced": False,
                "display_name": "Language Model",
                "dynamic": False,
                "info": "",
                "input_types": ["LanguageModel"],
                "list": False,
                "list_add_label": "Add More",
                "name": "llm",
                "override_skip": False,
                "placeholder": "",
                "required": True,
                "show": True,
                "title_case": False,
                "trace_as_metadata": True,
                "track_in_telemetry": False,
                "type": "other",
                "value": "",
            },
            "max_triplets_per_document": {
                "_input_type": "IntInput",
                "advanced": False,
                "display_name": "Max Triples Per Document",
                "dynamic": False,
                "info": "",
                "list": False,
                "list_add_label": "Add More",
                "name": "max_triplets_per_document",
                "override_skip": False,
                "placeholder": "",
                "required": False,
                "show": True,
                "title_case": False,
                "tool_mode": False,
                "trace_as_metadata": True,
                "track_in_telemetry": True,
                "type": "int",
                "value": 6,
            },
            "top_k": {
                "_input_type": "IntInput",
                "advanced": False,
                "display_name": "Top Graph Facts",
                "dynamic": False,
                "info": "",
                "list": False,
                "list_add_label": "Add More",
                "name": "top_k",
                "override_skip": False,
                "placeholder": "",
                "required": False,
                "show": True,
                "title_case": False,
                "tool_mode": False,
                "trace_as_metadata": True,
                "track_in_telemetry": True,
                "type": "int",
                "value": 8,
            },
        },
        position=(710, 340),
        measured=(360, 300),
        base_classes=["Message"],
    )

    prompt = clone_node(nodes_by_id, "Prompt Template-BBDFH", "Prompt Template-GRAPH1", "Graph Answer Prompt", (1110, 360))
    prompt["data"]["node"]["template"]["template"]["value"] = (
        "You are a QA knowledge assistant answering with graph-retrieved facts only.\\n"
        "Use the context below as your full source of truth.\\n\\n"
        "Context:\\n{context}\\n\\n"
        "Question:\\n{question}\\n\\n"
        "Rules:\\n"
        "1. Use only the graph facts above.\\n"
        "2. If the graph context is insufficient, reply exactly: I don't have enough graph context to answer that.\\n"
        "3. Reuse the [fact-n] citations when relevant.\\n"
        "4. Keep the answer concise and grounded."
    )
    prompt["data"]["node"]["custom_fields"]["template"] = ["context", "question"]

    answer_llm = clone_node(nodes_by_id, "OpenAIModel-Ui0z4", "OpenAIModel-GEN-GRAPH1", "Answer LLM", (1450, 400))
    answer_llm["data"]["node"]["template"]["model_name"]["value"] = "gpt-4o-mini"
    answer_llm["data"]["node"]["template"]["temperature"]["value"] = 0

    chat_output = clone_node(nodes_by_id, "ChatOutput-hRi1A", "ChatOutput-GRAPH1", "Chat Output", (1760, 400))

    nodes = [directory, graph_llm, chat_input, graph_engine, prompt, answer_llm, chat_output]
    edges = [
        make_edge(
            "Directory-GRAPH1",
            "Directory",
            "dataframe",
            ["DataFrame"],
            "CustomComponent-GRAPH1",
            "documents",
            ["Data", "DataFrame"],
            "other",
        ),
        make_edge(
            "OpenAIModel-GRAPH1",
            "OpenAIModel",
            "model_output",
            ["LanguageModel"],
            "CustomComponent-GRAPH1",
            "llm",
            ["LanguageModel"],
            "other",
        ),
        make_edge(
            "ChatInput-GRAPH1",
            "ChatInput",
            "message",
            ["Message"],
            "CustomComponent-GRAPH1",
            "question",
            ["Message"],
            "str",
        ),
        make_edge(
            "CustomComponent-GRAPH1",
            "CustomComponent",
            "context_message",
            ["Message"],
            "Prompt Template-GRAPH1",
            "context",
            ["Message"],
            "str",
        ),
        make_edge(
            "ChatInput-GRAPH1",
            "ChatInput",
            "message",
            ["Message"],
            "Prompt Template-GRAPH1",
            "question",
            ["Message"],
            "str",
        ),
        make_edge(
            "Prompt Template-GRAPH1",
            "Prompt Template",
            "prompt",
            ["Message"],
            "OpenAIModel-GEN-GRAPH1",
            "system_message",
            ["Message"],
            "str",
        ),
        make_edge(
            "ChatInput-GRAPH1",
            "ChatInput",
            "message",
            ["Message"],
            "OpenAIModel-GEN-GRAPH1",
            "input_value",
            ["Message"],
            "str",
        ),
        make_edge(
            "OpenAIModel-GEN-GRAPH1",
            "OpenAIModel",
            "text_output",
            ["Message"],
            "ChatOutput-GRAPH1",
            "input_value",
            ["Data", "DataFrame", "Message"],
            "other",
        ),
    ]

    return {
        "data": {
            "edges": edges,
            "nodes": nodes,
            "viewport": {"x": 498.0, "y": 162.0, "zoom": 0.7},
        },
        "description": (
            "Graph RAG for Langflow 1.7.x using a custom graph context engine, Directory loader, and OpenAI models."
        ),
        "endpoint_name": "graph-rag-pipeline",
        "id": "graph-rag-pipeline",
        "is_component": False,
        "last_tested_version": "1.7.2",
        "name": "Graph RAG Pipeline",
        "tags": ["rag", "graph", "langflow", "custom-component"],
    }


def main() -> None:
    jira_score = build_jira_story_score_flow()
    pdf_json = build_pdf_to_json_flow()
    jira_quickstart = build_jira_ticket_testplan_flow()
    quickstart = build_rice_pot_quickstart_flow()
    modular = build_modular_flow()
    graph = build_graph_flow()
    QUICKSTART_JIRA_SCORE_FLOW.write_text(json.dumps(jira_score, indent=2))
    QUICKSTART_PDF_JSON_FLOW.write_text(json.dumps(pdf_json, indent=2))
    QUICKSTART_JIRA_FLOW.write_text(json.dumps(jira_quickstart, indent=2))
    QUICKSTART_RICE_POT_FLOW.write_text(json.dumps(quickstart, indent=2))
    MODULAR_FLOW.write_text(json.dumps(modular, indent=2))
    GRAPH_FLOW.write_text(json.dumps(graph, indent=2))
    print(f"Updated {QUICKSTART_JIRA_SCORE_FLOW}")
    print(f"Updated {QUICKSTART_PDF_JSON_FLOW}")
    print(f"Updated {QUICKSTART_JIRA_FLOW}")
    print(f"Updated {QUICKSTART_RICE_POT_FLOW}")
    print(f"Updated {MODULAR_FLOW}")
    print(f"Updated {GRAPH_FLOW}")


if __name__ == "__main__":
    main()
