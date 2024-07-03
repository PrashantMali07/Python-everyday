'''
In this project we will play a game named "Russian roulette" using random number.

- Will create a list having option, number 1 to 5 and "BANG"
- we can run a for loop to get random result
- If result equals to "BANG", GAME OVER
'''
import random

options = list([1,2,3,4,5,"BANG"])

random.shuffle(options)

for i in range(6):
    result=options.pop()

    print(result)
    if "BANG"==result:
        print("You're dead :(")
        break