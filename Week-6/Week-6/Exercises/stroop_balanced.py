from expyriment import design, control, stimuli
from expyriment.misc.constants import C_WHITE, C_BLACK, K_r, K_g, K_o, K_b
import random
import itertools

""" Constants """
MATCHING = {K_r : 'red', K_o :'orange', K_b:'blue', K_g:'green'}
KEYS = MATCHING.keys()
COLORS = MATCHING.values()

N_BLOCKS = 8
N_TRIALS_IN_BLOCK = 16

INSTR_START = """
In this task, you have to indicate the color of the word as quick as possible.

Press the following keys:
R = RED
G = GREEN
B = BLUE
O = ORANGE

Once you are ready, press SPACE to continue.
"""
INSTR_MID = """You have finished half of the experiment, well done! Your task will be the same.\nTake a break then press SPACE to move on to the second half."""
INSTR_END = """Well done!\nPress SPACE to quit the experiment."""

FEEDBACK_CORRECT = """You got it correct """
FEEDBACK_INCORRECT = """You got it INcorrect """

""" Helper functions """
def load(stims):
    for stim in stims:
        stim.preload()

def timed_draw(*stims):
    t0 = exp.clock.time
    exp.screen.clear()
    for stim in stims:
        stim.present(clear=False, update=False)
    exp.screen.update()
    t1 = exp.clock.time
    return t1 - t0

def present_for(*stims, t=1000):
    dt = timed_draw(*stims)
    exp.clock.wait(t - dt)

def present_instructions(text):
    instructions = stimuli.TextScreen(text=text, text_justification=0, heading="Instructions")
    instructions.present()
    exp.keyboard.wait()

""" Global settings """
exp = design.Experiment(name="Stroop", background_colour=C_WHITE, foreground_colour=C_BLACK)
exp.add_data_variable_names(['block_cnt', 'trial_cnt', 'word', 'color', 'RT', 'correct'])

control.set_develop_mode()
control.initialize(exp)

""" Stimuli """
fixation = stimuli.FixCross()
fixation.preload()

stims = {w: {c: stimuli.TextLine(w, text_colour=c) for c in COLORS} for w in COLORS}
load([stims[w][c] for w in COLORS for c in COLORS])

feedback_correct = stimuli.TextLine(FEEDBACK_CORRECT)
feedback_incorrect = stimuli.TextLine(FEEDBACK_INCORRECT)
load([feedback_correct, feedback_incorrect])

""" Experiment """

def run_trial(block_id, trial_id, word, color):
    stim = stims[word][color]
    present_for(fixation, t=500)

    exp.keyboard.clear()
    
    stim.present()
    key, rt = exp.keyboard.wait(KEYS)

    chosen_col = MATCHING[key]
    correct = chosen_col == color

    exp.data.add([block_id, trial_id, word, color, rt, correct])
    feedback = feedback_correct if correct else feedback_incorrect
    present_for(feedback, t=1000)

control.start(subject_id=1)

balanced_color = design.permute.latin_square(list(COLORS), permutation_type = 'balanced')

present_instructions(INSTR_START)
for block in range(1, N_BLOCKS + 1):
    if block !=1:
        present_instructions(INSTR_MID)
    sequence = balanced_color[(block -1) % len(balanced_color)]
    trials = []
    for s in sequence:
        for i in range(4):
            word = random.choice(list(COLORS))
            trials.append((word, s))

    random.shuffle(trials)

    for trial, (word, color) in enumerate(trials, start = 1):
        run_trial(block, trial, word, color)

present_instructions(INSTR_END)

control.end()

