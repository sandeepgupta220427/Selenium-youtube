llm_response = "  The test PASSED with 95% confidence.  "

print(llm_response)
print(llm_response.strip())
print(llm_response.lower())
print(llm_response.upper())
print(llm_response.replace("PASSED", "FAILED"))
print(llm_response.replace("PASSED", "FAILED").strip().lower())

print("PASSED" in llm_response)
print("failed" in llm_response.lower())
