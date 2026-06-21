import json
# Parse JSON string into Python dictionary

api_response = '{"model": "claude", "score": 0.95, "passed": true}'
data = json.loads(api_response)

print(data)
print(data["model"]) 
# print(data.model) 
print(type(data))

# Convert Python dictionary back to JSON string

result = {"test": "hallucination", "score": 0.12}

json_string = json.dumps(result)
print(json_string)
print(type(json_string))
