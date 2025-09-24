
from expyriment import design, control, stimuli
import expyriment

control.set_develop_mode()
exp = expyriment.design.Experiment()

control.initialize(exp)

expyriment.control.start()

width = 800
height = 600
stim_lenth = width//10
stim_size = (stim_length,stim_length)

edges = []
for x in (-width,width):
    for y in (-height, h):
        edges.append((x//2, y //2))


left_down_rec = stimuli.Rectangle(size = (40, 40), colour = (255, 0, 0), position=(0, 0))
left_up_rec = stimuli.Rectangle(size = (40, 40), colour = (255, 0, 0), position=(0,200))
right_up_rec = stimuli.Rectangle(size = (40, 40), colour = (255, 0, 0), position=(200, 0))
right_down_rec = stimuli.Rectangle(size = (40, 40), colour = (255, 0, 0), position=(200, 200))

left_down_rec.present(clear=False, update = False)
left_up_rec.present(clear=False, update = False)
right_down_rec.present(clear=False, update = False)
right_up_rec.present(clear=False, update = False)
control.end()

squares = [stimuli.Rectangle(position = ) for position in positions]