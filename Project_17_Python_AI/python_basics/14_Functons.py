def run_test(testname, expected, actual):
    """
    This is a multi comment
    """
    if expected == actual:
        print(f"{testname} PASSED")
    else:
        print(f"{testname} FAILED")


run_test("Test 1", 10, 10)
run_test("Test 2", 10, 20)

# Default Parameters and Keyword Arguments in Functions

def call_llm(prompt, model="gpt-4", temperature=0.7, max_tokens=100):
    print(f"  Calling {model} (temp={temperature}, max_tokens={max_tokens})")
    print(f"  Prompt: {prompt[:50]}...")
    return f"Response from {model}"


response = call_llm("Hello, how are you?")
print(response)

response2 = call_llm("Hello, how are you?", model="gpt-5", temperature=0.9, max_tokens=200)
print(response2)

call_llm("Summarize this bug report")              # Uses all defaults
call_llm("Summarize this", model="gpt-4")          # Override just the model
call_llm("Summarize this", temperature=0.0)         # Override just temperature
call_llm("Summarize this", max_tokens=2048, temperature=0.3)  # Override multiple