from expyriment import design, control, stimuli

control.set_develop_mode()

exp = design.Experiment(name = 'Two squares')

control.initialize(exp)
size = (50, 50)

left_square = stimuli.Rectangle(size = size, colour = (255,0,0), position = (-100,0))
right_square = stimuli.Rectangle(size = size, colour =(0, 255, 0), position = (100,0))

control.start(subject_id=1)

left_square.present(clear = True, update=False)
right_square.present(clear = False, update=False)