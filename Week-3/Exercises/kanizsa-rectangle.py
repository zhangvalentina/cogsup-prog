
from expyriment import design, control, stimuli
import expyriment

def kanizsa_rectangle(asp_ratio= 1, rec_scale = 0.25, cir_scale=0.05):
    control.set_develop_mode()
    exp = expyriment.design.Experiment(background_colour = (128,128,128)) 
    control.initialize(exp)
    expyriment.control.start()
    exp.screen.clear()
    
    width, height = exp.screen.size
    rect_width = int(width* rec_scale)
    rect_length = int(rect_width / asp_ratio)
    circle_radius = int(width * cir_scale)
    
    w = rect_width // 2 
    h = rect_length // 2

# compute the positions for 4 circles
    edges = []
    for x in (-w ,w):
        for y in (-h, h): 
            edges.append((x,y))
        
# based on the position (index of tuple), present squares with different colours and rotation angle        
    for x, y in edges:
        if y > 0:
            colour = (0,0,0)
        elif y < 0:
            colour = (255,255,255)
        circle = stimuli.Circle(radius = circle_radius, colour = colour, position = (x,y))
        circle.present(clear = False, update = False) # do not clear the screen so all squares appear at the same time

        if x < 0 and y < 0 :
            mask = stimuli.Rectangle(size = (circle_radius,circle_radius), colour = (128, 128, 128), position = (x + circle_radius//2, y + circle_radius//2))
        elif x > 0 and y < 0:
            mask = stimuli.Rectangle(size = (circle_radius,circle_radius), colour = (128, 128, 128), position = (x - circle_radius//2, y + circle_radius//2))
        elif x< 0 and y > 0:
            mask = stimuli.Rectangle(size = (circle_radius,circle_radius), colour = (128, 128, 128), position = (x + circle_radius//2, y - circle_radius//2))
        else:
            mask = stimuli.Rectangle(size = (circle_radius,circle_radius), colour = (128, 128, 128), position = (x - circle_radius//2, y - circle_radius//2))

        mask.present(clear = False, update = False) # do not clear the screen so all squares appear at the same time

    exp.screen.update()
    exp.clock.wait(2000) # for 2 seconds
    control.end()

kanizsa_rectangle(asp_ratio=2.0, rec_scale=0.3, cir_scale=0.06)

