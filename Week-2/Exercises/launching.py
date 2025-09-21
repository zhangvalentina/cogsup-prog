from expyriment import design, control, stimuli # import packadge

control.set_develop_mode() # skip the intro

exp = design.Experiment(name = 'Two squares') # create experiment and give a title

control.initialize(exp) # initiate experiment
size = (50, 50) # squere's default size

left_square = stimuli.Rectangle(size = size, colour = (255,0,0), position = (-400,0)) # create a red square on the left
right_square = stimuli.Rectangle(size = size, colour =(0, 255, 0), position = (0,0)) # create a green square on the right

control.start(subject_id=1) # set the participant's id

left_square.present(clear = True, update=False) # present the left square
right_square.present(clear = False, update=False) # present the right square
exp.clock.wait(1000) # wait for 1 second

steps = 35 # number of steps
left_start = -400 # position of starting point of red square
left_end = -50 # position of ending point of red square
right_start = 0 # position of starting point of green square
right_end = 350 # position of ending point of green square

left_dx = (left_end - left_start) / steps # calculate the single  movement for red square
right_dx = (right_end - right_start) / steps # calculate the single  movement for red square

for i in range(steps):
    left_square.move((left_dx, 0))     # move the red square to the right
    left_square.present(clear=True, update=False) # present the red square and clearing the previous ones
    right_square.present(clear=False, update=True)  # the green one on the right stays there

for i in range(steps): # once the left one 'touch' the right one, it starts to move
    left_square.present(clear=True, update=False)   # the left one stays in the middle
    right_square.move((right_dx, 0))  # the right one moves toward right
    right_square.present(clear=False, update=True) # it reaches to the edge and stays there

left_square.present(clear=True, update=False) # present the left square
right_square.present(clear=False, update=True) # present the right square
exp.clock.wait(1000) # the image displays for 1 second