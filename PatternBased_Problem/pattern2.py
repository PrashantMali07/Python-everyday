'''
Write a Python program to create inverted star pattern

*****
 ****
  ***
   **
    *
'''

n = int(input("Enter the number of rows = "))

for i in range(n, 0, -1):
    print((n-i) * ' ' + i * '*')


## Creating a function for the same pattern
def inverted_star_pattern_recursive(height):
    if height > 0:
        print("*" * height)
        inverted_star_pattern_recursive(height - 1)