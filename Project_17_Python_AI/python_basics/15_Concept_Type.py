def calculate(passed , total):
    return (passed / total) * 100

result = calculate(80, 100)
print(result)


# Strict Type - Python 3.X
def calculate(passed : float , total :float) -> float:
    return (passed / total) * 100


result = calculate(80, 100)
print(result)

def evaluate_test(
    test_name : str,
    score : float, 
    threshold : float, 
    passed  : bool) -> dict:
    return {
        "test_name": test_name,
        "score": score,
        "threshold": threshold,
        "passed": passed
    }


r = evaluate_test("Test 1", 80, 70, True)  
print(r)









