from expyriment import design, control, stimuli
import random

def load(stims):
    for stim in stims:
        stim.preload()
    pass

def timed_draw(stims, canvas):
    t0 = exp.clock.time()
    canvas.preload()

    for stim in stims:
        stim.plot(canvas)

    canvas.present()
    t1 = exp.clock.time()
    duration_draw = (t1 - t0)/1000

    return duration_draw
    # return the time it took to draw

def present_for(stims, duration_draw, t=1000):
    for stim in stims:
        stim.present(clear = False, update = True)
    exp.clock.wait(t-duration_draw)    
    pass


""" Test functions """
exp = design.Experiment()

control.set_develop_mode()
control.initialize(exp)

fixation = stimuli.FixCross()
load([fixation])

n = 20
positions = [(random.randint(-300, 300), random.randint(-300, 300)) for _ in range(n)]
squares = [stimuli.Rectangle(size=(50, 50), position = pos) for pos in positions]
load(squares)

durations = []

t0 = exp.clock.time
for square in squares:
    if not square.is_preloaded:
        print("Preloading function not implemneted correctly.")
    stims = [fixation, square] 
    present_for(stims, 500)
    t1 = exp.clock.time
    durations.append(t1-t0)
    t0 = t1

print(durations)

control.end()