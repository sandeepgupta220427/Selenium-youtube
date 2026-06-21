# Dictionaries — Key-Value Pairs (JSON-like)
llm_config = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
}

print(llm_config)
print(type(llm_config))

print(llm_config["model"])
print(llm_config["temperature"])
print(llm_config["max_tokens"])

llm_config["max_tokens"] = 2000
print(llm_config)


# mcp_config: 
# "mcp-atlassian": {
#             "command": "uvx",
#             "args": [
#                 "mcp-atlassian"
#             ],
#             "env": {
#                 "JIRA_URL": "https://your-company.atlassian.net",
#                 "JIRA_USERNAME": "your.email@company.com",
#                 "JIRA_API_TOKEN": "your_api_token",
#                 "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
#                 "CONFLUENCE_USERNAME": "your.email@company.com",
#                 "CONFLUENCE_API_TOKEN": "your_api_token"
#             }
#         }
#     }

eval_result = {
    "test_name": "hallucination_check",
    "metrics": {
        "hallucination_score": 0.12,
        "relevance_score": 0.89,
        "coherence_score": 0.95
    },
    "verdict": "PASS"
}
hall_score = eval_result["metrics"]["hallucination_score"]
print(f"Hallucination score: {hall_score}")


print("  --------   ")
details_pramod = {
    "name" : "Pramod",
    "age" : 65,
    "city" : "Bangalore",
    "skills" : ["Python", "AI", "ML"],
    "is_employed" : True
}

print(details_pramod)
print(details_pramod["name"])
print(details_pramod["age"])
print(details_pramod["city"])
print(details_pramod["skills"])
print(details_pramod["is_employed"])