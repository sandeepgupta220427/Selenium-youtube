user_input = input("Enter your age: ")
print(user_input)
print(type(user_input))

age = int(user_input)

if age > 18:
    print("You are eligible for voting")
else:
    print("You are not eligible for voting")


# Lambda Function   
result = lambda age : "Eligible" if age > 18 else "Not Eligible"
print(result(age))
