from expyriment import design, control, stimuli
from expyriment.misc.constants import C_WHITE, C_BLACK, K_a, K_DOWN, K_UP, K_LEFT, K_RIGHT


""" Global settings """
exp = design.Experiment(name="Blindspot", background_colour=C_WHITE, foreground_colour=C_BLACK)
control.set_develop_mode()
control.initialize(exp)

""" Stimuli """
def make_circle(r, pos=(0,0)):
    position = list(pos)
    c = stimuli.Circle(r, position=tuple(position), anti_aliasing=10)
    c.preload()
    return c, pos, r

""" Experiment """
def run_trial():
    fixation = stimuli.FixCross(size=(150, 150), line_width=10, position=[300, 0])
    fixation.preload()

    radius = 75
    circle, position, r = make_circle(radius)

    while True:
        fixation.present(clear = True, update= False)
        circle.present(clear = False, update = True)
        key = exp.keyboard.check(key = [K_1,K_2,K_DOWN, K_UP, K_LEFT, K_RIGHT])
        if key == K_DOWN:
            position[1] -= 4
        if key == K_UP:
            position[1] += 4
        if key == K_LEFT:
            position[0] -= 4
        if key == K_RIGHT:
            position[0] += 4  
        if key == K_1:
            r -= 5
        if key == K_2:
            r += 5
        exp.keyboard.wait()
        circle, position, r = make_circle(r, position)



control.start(subject_id=1)

run_trial()
    
control.end()
