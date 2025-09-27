
from expyriment import design, control, stimuli
import expyriment

control.set_develop_mode()
exp = expyriment.design.Experiment()

control.initialize(exp)

expyriment.control.start()

width, height = exp.screen.size # get the size of the screen
stim_length = width//20 # int
stim_size = (stim_length,stim_length) # set the square's size

w = width // 2 # find the coordinates of 4 corners
h = height // 2

edges = []
for x in (-w ,w):
    for y in (-h, h): # loop over the 4 corners
        # push the squares toward the center, for x on the right side, substract half the square width to move left and vice versa; same for the y
        edge_x = x - (stim_length//2 if x> 0 else -stim_length//2)
        edge_y = y - (stim_length//2 if y> 0 else - stim_length//2)
        # save the adjusted corner coordinates so they are not the corners but the center of squares
        edges.append((edge_x, edge_y))
        

squares = []
for i in edges:
    square = stimuli.Rectangle(size = stim_size, colour = (255, 0,0), position = i, line_width = 2)
    squares.append(square)
    square.present(clear = False, update = False) # do not clear the screen so all squares appear at the same time

exp.screen.update()
exp.clock.wait(2000) # for 2 seconds


control.end()

