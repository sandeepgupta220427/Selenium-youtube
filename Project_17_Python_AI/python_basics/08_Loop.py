models = ["gpt-4", "claude-sonnet", "gemini-pro"]
test_results = ["PASS", "FAIL", "PASS", "PASS", "FAIL"]
scores = [0.9, 0.3, 0.85, 0.45, 0.72]
test_steps = ["login", "navigate", "click_button", "verify"]

# this is comment in python, this code will not be executed.
# Iterate over them

for model in models:
    print(model)

print("---------")

# range(3) -> 0,1,2
print(models[0])
print(models[1])
print(models[2])


for i in range(3):
    print(models[i])

print("---------")


for result in test_results:
    print(result)

print("---------")


for score in scores:
    print(score)

print("---------")

for step in test_steps:
    print(step)