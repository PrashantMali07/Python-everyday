'''
1. Variables are containers for storing data values.
2. Variables do not need to be declared with any particular type, and can even change type after they have been set
3. If you want to specify the data type of a variable, this can be done with casting.
4. Get the Type; You can get the data type of a variable with the type() function.
5. String variables can be declared either by using single or double quotes, is same
6. Variable names are case-sensitive.
'''

# defining a variable

a=1
b=2

# printing those values
print("a = ", a)
print("b = ", b)

# we can also store string and character
x='J' # it is type of string, we can check the same using function type()
y='Hello World!!' # its obviously string

print("Character stored in variable 'x' ", x)
print("String stored in variable 'y' ", y)

# type function

print(type(a))
print(type(x))

# case sensitive, This will create two variables

m = 6
M = 10

print(m)
print(M)

'''
 A variable can have a short name (like x and y) or a more descriptive name (age, carname, total_volume). Rules for Python variables:

    A variable name must start with a letter or the underscore character
    A variable name cannot start with a number
    A variable name can only contain alpha-numeric characters and underscores (A-z, 0-9, and _ )
    Variable names are case-sensitive (age, Age and AGE are three different variables)
    A variable name cannot be any of the Python keywords.

'''

# Legal variable names:

myvar = "John"
my_var = "John"
_my_var = "John"
myVar = "John"
MYVAR = "John"
myvar2 = "John"

# Illegal variable names: will throw error; invalid syntax

2myvar = "John"
my-var = "John"
my var = "John"

# Python allows you to assign values to multiple variables in one line:

x, y, z = "Orange", "Banana", "Cherry"
print(x)
print(y)
print(z)

# And you can assign the same value to multiple variables in one line:

x = y = z = "Orange"
print(x)
print(y)
print(z)

# If you have a collection of values in a list, tuple etc. Python allows you to extract the values into variables. This is called unpacking.

fruits = ["apple", "banana", "cherry"]
x, y, z = fruits
print(x)
print(y)
print(z)

# Global & Local variable

'''
If you create a variable with the same name inside a function, this variable will be local, and can only be used inside the function. The global variable with the same name will remain as it was, global and with the original value.


Create a variable inside a function, with the same name as the global variable
'''

x = "awesome" # this is a global variable

def myfunc():
  x = "fantastic" # this is local variable.
  print("Python is " + x)

myfunc()

print("Python is " + x) 



'''
Create a variable outside of a function, and use it inside the function
'''
x = "awesome"

def myfunc():
  print("Python is " + x)

myfunc() 

# Also, use the global keyword if you want to change a global variable inside a function.

x = "awesome"

def myfunc():
  global x
  x = "fantastic"

myfunc()

print("Python is " + x)

