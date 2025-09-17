from expyriment import design, control, stimuli

control.set_develop_mode()

exp = design.Experiment(name = 'Circle')

# Initialize the experiment: Must be done before presenting any stimulus
control.initialize(exp)

square = stimuli.Rectangle(size = (50, 50), colour = (0, 0, 255))

# Create a fixation cross (color, size, and position will take on default values)
fixation = stimuli.FixCross() # At this stage the fixation cross is not yet rendered

# Start running the experiment
control.start(subject_id=1)

square.present(clear=True, update=False)

fixation.present(clear=False, update=True)

exp.clock.wait(500)

square.present(clear=True, update=True)

exp.keyboard.wait(duration = 500)

# End the current session and quit expyriment
control.end()