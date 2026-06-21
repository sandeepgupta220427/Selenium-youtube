test_results = ["PASS", "FAIL", "PASS", "PASS", "FAIL"]

fail_count = 0
for result in test_results:
    if result == "FAIL":
        fail_count += 1

print(f"Failed: {fail_count} out of {len(test_results)}")

models = ["gpt-4", "claude-sonnet", "gemini-pro"]
for model in models:
    print(f"Model : {model}")

# +=
# -= 
# ++I - No Incremnt in Python
# --I - No Decremnt in Python
# I++ - No Incremnt in Python
# I-- - No Decremnt in Python

a = 10
a += 1 # a = a + 1
print(a)

a -= 2 # a = a - 1
print(a)

# --, ++ there is no concept in python
