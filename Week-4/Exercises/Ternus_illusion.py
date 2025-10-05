# global setting
# stimulus generation
# trial run

from expyriment.misc.constants import K_SPACE
from expyriment import design, control, stimuli
import expyriment

control.set_develop_mode()
exp = expyriment.design.Experiment(background_colour = (225,225,225))
control.initialize(exp)
expyriment.control.start(exp)

def make_circles(radius, colour = False):
    circle_centered = stimuli.Circle(radius = radius, colour = (0,0,0), position = (0,0))
    circle_left = stimuli.Circle(radius = radius, colour = (0,0,0), position = ((-radius*2 - 10), 0))
    circle_right = stimuli.Circle(radius = radius, colour = (0,0,0), position = ((radius*2 + 10), 0))
    
    if colour:
        add_tags(circle_left,circle_centered,circle_right)

    canvas_left = stimuli.Canvas(size = exp.screen.size)
    circle_centered.plot(canvas_left)
    circle_left.plot(canvas_left)

    canvas_right = stimuli.Canvas(size = exp.screen.size)
    circle_centered.plot(canvas_right)
    circle_right.plot(canvas_right)

    return canvas_left, canvas_right, circle_centered, circle_left, circle_right


def present_for(canvas_left, canvas_right, ISI = 40):
    first = 'left'
    blank = stimuli.Canvas(size = exp.screen.size)

    while True:
        if first == 'left':
            canvas_left.present(clear = True, update = True)
            exp.clock.wait(200)
        else:
            canvas_right.present(clear = True, update = True)
            exp.clock.wait(200)

        blank.present()
        exp.clock.wait(ISI)

        if first == 'left':
            first = 'right'
        else:
            first = 'left'

        if exp.keyboard.check(K_SPACE):
            break
    

def add_tags(circle_left, circle_centered, circle_right, left_colour = (255,0,0), centered_colour = (100,250,0), right_colour = (0,0,150)):
    if circle_left.position[0] < 0:
        circle_left.colour = left_colour
    else: 
        circle_left.colour = (0,0,0)
    if circle_centered.position[0] == 0:
        circle_centered.colour = centered_colour
    else:
        circle_centered.colour = (0,0,0)
    if circle_right.position[0] > 0:
        circle_right.colour = right_colour
    else:
        circle_right.colour = (0,0,0)



canvas_left, canvas_right, circle_left, circle_right, circle_centered = make_circles(20, colour = False)
present_for(canvas_left, canvas_right, ISI = 40)
present_for(canvas_left, canvas_right, ISI = 100)
add_tags(circle_left,circle_centered, circle_right)
canvas_left, canvas_right, circle_left, circle_right, circle_centered = make_circles(20, colour = True)
present_for(canvas_left, canvas_right, ISI = 50)

