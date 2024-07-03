# importing the random library
import random

x = random.randint(10,99)

print("The random number is ",x)

# generating a list of 10 random float numbers, using list comprehension

lst = [round(random.uniform(10.2, 30.6),2) for i in range(10)]
print("List of 10 random numbers: ", lst)

# generating a list of 10 random integer numbers, using list comprehension

lst1 = [random.randint(10, 30) for i in range(10)]
print("List of 10 random numbers: ", lst1)