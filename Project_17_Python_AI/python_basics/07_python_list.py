test_results = ["PASS", "FAIL", "PASS", "PASS", "FAIL"]
print(test_results)
print(test_results[0])
print(test_results[1])
print(test_results[2])
print(test_results[3])
print(test_results[4])
print(test_results[-1])
print(test_results[-2])
print(test_results[-3])
print(test_results[-4])
print(test_results[-5])

fruits = ["apple", "banana", "cherry"]
print(fruits)

mix_list = [1, "apple", 0.5, True, None]
print(mix_list)

print(len(test_results))
print(len(fruits))
print(len(mix_list))

# list functions

test_results.append("PASS")
print(test_results)

test_results.remove("FAIL")
print(test_results)

test_results.pop()
print(test_results)

test_results.insert(0, "FAIL")
print(test_results)

test_results.sort()
print(test_results)

test_results.reverse()
print(test_results)

test_results.count("PASS")
print(test_results)

test_results.index("PASS")
print(test_results)

test_results.copy()
print(test_results)

test_results.clear()
print(test_results)