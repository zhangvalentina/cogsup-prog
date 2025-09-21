"""
Have a look at the script called 'human-guess-a-number.py' (in the same folder as this one).

Your task is to invert it: You should think of a number between 1 and 100, and the computer 
should be programmed to keep guessing at it until it finds the number you are thinking of.

At every step, add comments reflecting the logic of what the particular line of code is (supposed 
to be) doing. 
"""
print("Please think of a number between 1 and 100")

low = 1 # set the lowest
high = 100  # set the highest
guess = (low + high) // 2  # the median as the first guess 

while True: # loop
    print(f"My guess is {guess}.") # give a guess
    
    answer = input("Is it correct (c), too low (l), or too high (h)? ").lower() # ask participant to give a feedback by giving an input, transformed into lower case
    
    if answer == 'c': # if participant indicated that the guess was correct then the loop breaks
        print(f"The number was {guess}.")
        break
    elif answer == 'l': # or, if they indicate the guess was smaller than the true number
        low = guess + 1 # set the lowest boundery to the guess + 1
    elif answer == 'h': # or, if they indicate the guess was bigger than the true number
        high = guess - 1  #set the lowest boundery to the guess - 1
    else: # if they did not enter any of these letters, print the text again
        print("Please type 'c', 'l', or 'h'.")
    
    guess = (low + high) // 2 # update the median/guess based on the new thresholds
