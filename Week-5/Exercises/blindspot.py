from expyriment import design, control, stimuli
from expyriment.misc.constants import C_WHITE, C_BLACK, K_r,K_l, K_DOWN, K_UP, K_LEFT, K_RIGHT, K_1, K_2, K_SPACE


""" Global settings """
exp = design.Experiment(name="Blindspot", background_colour=C_WHITE, foreground_colour=C_BLACK)
control.set_develop_mode()
control.initialize(exp)

""" Stimuli """
def make_circle(r, pos=(0,0)):
    position = list(pos)
    c = stimuli.Circle(r, position=tuple(position), anti_aliasing=10)
    c.preload()
    return c

""" Experiment """
def run_trial():
    exp.add_data_variable_names(['tested_eye', 'circle radius','key_press' 'circle_x','circle_y'])
    instru = stimuli.TextScreen(
        text = 'To find the blind spot, chose the eye you want to test and close the other eye. '
                'Fixate on the cross on the screen and adjust the position of the cicle using arrows, until you cannot see the circle.'
                'You can also adjust the size of the circle with 1 = smaller, 2 = larger' 
                'When you are done, you can press SPACEBAR to move on. Good luck!', 
                heading = 'Welcome'
    )
    instru.present(clear = True, update = True)
    exp.keyboard.wait(keys = [K_SPACE])
    
    ins_eye = stimuli.TextScreen(
        text = 'Do you want to find the blindspot in your left (press L) or right (press R) eye ?', 
        heading = 'Please indicate the eye you want to test'
    )
    ins_eye.present(clear = True, update = True)
    eye, rt = exp.keyboard.wait(keys =[K_r, K_l])
    
    r = 75
    if eye == K_r:
        fixation_pos = [-300, 0]
        circle_pos = [300, 0]
        tested_eye = 'R'
        key_press = 'right'
    elif eye == K_l:
        fixation_pos = [300, 0]
        circle_pos = [-300, 0]
        tested_eye = 'L'
        key_press = 'left'

    
    fixation = stimuli.FixCross(size=(150, 150), line_width=10, position=fixation_pos)
    fixation.preload()
    circle = make_circle(r, circle_pos)

    exp.data.add([tested_eye,r,key_press, circle_pos[0],circle_pos[1]])
    while True:
        exp.screen.clear()
        fixation.present(clear = False, update= False)
        circle.present(clear = False, update = True)
        
        key, rt = exp.keyboard.wait(keys = [K_1,K_2,K_DOWN, K_UP, K_LEFT, K_RIGHT, K_SPACE])
        if key == K_DOWN:
            circle_pos[1] -= 4
            key_press = 'down'
            exp.data.add([tested_eye, r, key_press, circle_pos[0], circle_pos[1]])
        if key == K_UP:
            circle_pos[1] += 4
            key_press = 'up'
            exp.data.add([tested_eye, r,key_press, circle_pos[0], circle_pos[1]])
        if key == K_LEFT:
            circle_pos[0] -= 4
            key_press = 'left'
            exp.data.add([tested_eye, r, key_press,circle_pos[0], circle_pos[1]])
        if key == K_RIGHT:
            circle_pos[0] += 4  
            key_press = 'right'
            exp.data.add([tested_eye, r, key_press,circle_pos[0], circle_pos[1]])
        if key == K_1:
            r -= 5
            key_press = 'smaller'
            exp.data.add([tested_eye, r, key_press,circle_pos[0], circle_pos[1]])
        if key == K_2:
            r += 5
            key_press = 'larger'
            exp.data.add([tested_eye, r, key_press,circle_pos[0], circle_pos[1]])
        if key == K_SPACE:
            break
        circle = make_circle(r, circle_pos)



control.start(subject_id=1)

run_trial()
    
control.end()

