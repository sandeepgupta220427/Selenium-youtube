# You need to create a program which will
#  take the user input of the name, age,
#  and phone number. 
# After that, you need to verify if the age is greater than 18,
#  he can vote and you need to print the age also in this case. 


name = input("Enter your name: ")
age = int(input("Enter your age: "))
phone_number = str(input("Enter your phone number: "))

if age >= 18:
    print("You are eligible for voting")
    print("Your age is", age)
    print("Your phone number is", phone_number)
else:
    print("You are not eligible for voting")
