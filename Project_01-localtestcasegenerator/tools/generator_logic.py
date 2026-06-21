import json
import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError

class TestCase(BaseModel):
    id: str
    title: str
    description: str
    preconditions: List[str] = Field(default_factory=list)
    steps: List[str]
    expected_result: str
    priority: str
    type: str

class TestSuite(BaseModel):
    test_cases: List[TestCase]

SYSTEM_PROMPT = """
You are an expert QA Engineer. Your task is to generate comprehensive software test cases based on the user's input.

RULES:
1. Output MUST be valid JSON only. Do not add any conversational text before or after.
2. The JSON structure must be a list of objects exactly matching this schema:
[
  {
    "id": "TC-001",
    "title": "Concise title",
    "description": "What is being tested",
    "preconditions": ["Condition 1", "Condition 2"],
    "steps": ["Step 1", "Step 2"],
    "expected_result": "Exact expected outcome",
    "priority": "High | Medium | Low",
    "type": "Functional | Neural | API | UI"
  }
]
3. Generate at least 3 distinct test cases (Positive, Negative, Boundary) if applicable.
4. If the user input is code, analyze logical paths.
"""

def clean_json_string(raw_text: str) -> str:
    """
    Strips markdown code fences and extraneous text to extract just the JSON.
    """
    # Remove markdown code blocks if present
    match = re.search(r'```json\s*(.*?)```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback: Try to find the first [ and last ]
    start = raw_text.find('[')
    end = raw_text.rfind(']')
    if start != -1 and end != -1:
        return raw_text[start:end+1]
        
    return raw_text

def validate_test_cases(json_str: str) -> List[Dict[str, Any]]:
    """
    Parses and validates the JSON using Pydantic.
    """
    try:
        clean_text = clean_json_string(json_str)
        data = json.loads(clean_text)
        
        # Validate list structure
        if not isinstance(data, list):
            raise ValueError("Output is not a JSON list")
            
        validated_cases = []
        for item in data:
            # Pydantic validation
            tc = TestCase(**item)
            validated_cases.append(tc.model_dump())
            
        return validated_cases
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format from LLM: {str(e)}")
    except ValidationError as e:
        raise ValueError(f"Schema Validation Failed: {str(e)}")
