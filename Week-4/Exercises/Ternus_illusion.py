# global setting
# stimulus generation
# trial run

from expyriment.misc.constants import K_SPACE
from expyriment import design, control, stimuli
import expyriment
from drawing_functions import load, timed_draw, present_for

control.set_develop_mode()
present_for(exp, circles, num_frames=12)        
exp = design.Experiment(background_colour=C_WHITE, foreground_colour=C_BLACK)
control.initialize(exp)
control.start(subject_id=1)
# def make_circles(radius, colour = False):
#    circle_centered = stimuli.Circle(radius = radius, colour = (0,0,0), position = (0,0))
#    circle_left = stimuli.Circle(radius = radius, colour = (0,0,0), position = ((-radius*2 - 10), 0))
#    circle_right = stimuli.Circle(radius = radius, colour = (0,0,0), position = ((radius*2 + 10), 0))
#    
#    if colour:
#        add_tags(circle_left,circle_centered,circle_right)

#    canvas_left = stimuli.Canvas(size = exp.screen.size)
#    circle_centered.plot(canvas_left)
#    circle_left.plot(canvas_left)

#    canvas_right = stimuli.Canvas(size = exp.screen.size)
#    circle_centered.plot(canvas_right)
#    circle_right.plot(canvas_right)

#    return canvas_left, canvas_right, circle_centered, circle_left, circle_right 

RADIUS =50; DISTANCE = RADIUS*3; SPREAD = RADIUS *9
def make_circles(radius=RADIUS):
    positions = range(-SPREAD //2, SPREAD //2, DISTANCE)
    circles = [stimuli.Circle(radius= radius,position = (x_pos,0)) for x_pos in positions]
    return circles

def present_time(canvas_left, canvas_right, ISI = 40):
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

#def add_tags(circle_left, circle_centered, circle_right, left_colour = (255,0,0), centered_colour = (100,250,0), right_colour = (0,0,150)):
#    if circle_left.position[0] < 0:
#        circle_left.colour = left_colour
#    else: 
#        circle_left.colour = (0,0,0)
#    if circle_centered.position[0] == 0:
#        circle_centered.colour = centered_colour
#    else:
#        circle_centered.colour = (0,0,0)
#    if circle_right.position[0] > 0:
#        circle_right.colour = right_colour
#    else:
#        circle_right.colour = (0,0,0)
def add_tags(circles, tag_radius):
    tag_colors = [C_YELLOW, C_RED, C_BLUE]
    tag_circles = [stimuli.Circle(radius=tag_radius, colour=col) for col in tag_colors]
    for circle, tag in zip(circles, tag_circles):
        tag.plot(circle)

""" Inside your run_trial function """
circles = make_circles()
if tags: add_tags(circles, tag_radius=RADIUS // 5)
load(circles)


#canvas_left, canvas_right, circle_left, circle_right, circle_centered = make_circles(20, colour = False)
#present_for(canvas_left, canvas_right, ISI = 40)
#present_for(canvas_left, canvas_right, ISI = 100)
#add_tags(circle_left,circle_centered, circle_right)
#canvas_left, canvas_right, circle_left, circle_right, circle_centered = make_circles(20, colour = True)
#present_for(canvas_left, canvas_right, ISI = 50)

def run_trial(circle_frames=12, ISI=0, tags=False): 
    # Create circles 
    circles = make_circles() 
    load(circles) 

    if tags: 
        add_tags(circles, tag_radius=RADIUS // 5) 
    
    extent = RADIUS *2
    while True: 
        for dx in (extent, -extent): 
            present_for(exp, circles, num_frames=circle_frames) 
            present_for(exp, [], num_frames=ISI) 
            circles[0].move((dx, 0)) 
        if exp.keyboard.check(K_SPACE): 
            break
        

trials = [{'ISI': 0}, {'ISI': 18}, {'ISI': 18, 'tags': True}]
for trial_params in trials:
    run_trial(**trial_params)
control.end()