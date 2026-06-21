test_prompt = "Act as a QA give me the Test plan for the app.vwo.com"
print(test_prompt)

model_name = "gpt-4"

expected_output = 'The response should contain a "status" field'

print(type(test_prompt))
print(type(model_name))
print(type(expected_output))

x = 10
print(type(x))

y = 10.5
print(type(y))

z = True
print(type(z))

a = None
print(type(a))

# Numbers
max_retries = 3              # int
temperature = 0.7            # float (you'll see this in every LLM config)
confidence_threshold = 0.85  # float

# Booleans
is_hallucination = False
test_passed = True

# None — represents "no value" (like null in Java/JavaScript)
api_key = None