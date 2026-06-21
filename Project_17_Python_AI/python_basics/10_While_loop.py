# while loop — repeat until a condition is met

retries = 0
max_retries = 3

while retries < max_retries:
    print(f"Retry {retries + 1}...")
    retries += 1

print("Done!")

scores = [0.9, 0.3, 0.85, 0.45, 0.72]
passing_scores = []
for s in scores:
    if s >= 0.7:
        passing_scores.append(s)

print(passing_scores)

test_steps = ["login", "navigate", "click_button", "verify"]

test_steps[0]     # "login"
test_steps[-1]


test_steps.append("screenshot")     # "verify" (last element)
test_steps.insert(2, "wait_for_load") 
test_steps.remove("click_button")
test_steps.pop()
print(test_steps)
