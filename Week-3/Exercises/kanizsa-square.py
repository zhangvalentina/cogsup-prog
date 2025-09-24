
from expyriment import design, control, stimuli
import expyriment

control.set_develop_mode()
exp = expyriment.design.Experiment(background_colour = C_GREY)

control.initialize(exp)

expyriment.control.start()

width = 800
height = 600
rec_lenth = 200
radius = 40
stim_size = (rec_length, rec_length)
circle = stimuli.Circle(radius = radius)

for x in (-width,width):
    for y in (-height, height):
        edges.append((x//2, y //2))

rect_length = 