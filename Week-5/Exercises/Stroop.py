from expyriment import design, control, stimuli
from expyriment.misc.constants import C_WHITE, C_BLACK, C_RED, C_BLUE, C_GREEN, K_s,K_k, K_SPACE
from expyriment.misc import Colour
import random

exp = design.Experiment(name="Stroop effect", background_colour=C_WHITE, foreground_colour=C_BLACK)
control.set_develop_mode()
control.initialize(exp)

trial_n = 20
trial_n = int(trial_n)
block_n = 2
block_n = int(block_n)
exp.add_data_variable_names(['trial block', 'trial number', 'trial type','word meaning','text color', 'RTs','accuracy'])
C_ORANGE = Colour((255,165,0))

instru = stimuli.TextScreen(
    text = 'Please indicate as quick as possible whether the color and the meaning of the word matches. \n Press [S] if they match. Press [K] if they do not match). \n There are 2 blocks of 10 trials per each. \n After each trial you will receive the feedback. \n You can press SPACEBAR to move on. Good luck!', 
                heading = 'Welcome'
)
instru.present(clear = True, update = True)
exp.keyboard.wait(keys = [K_SPACE])

words = ['red','blue','green','orange']
colors = [C_RED,C_BLUE,C_GREEN,C_ORANGE]

control.start(subject_id = 1)

for block in range(1, block_n+1):
    block_ins = stimuli.TextLine(text  = 'Take a short break. Press SPACE to begin this block')
    block_ins.present(clear = True, update = True)
    exp.keyboard.wait(keys =[K_SPACE])
    for trial in range(1, trial_n // block_n + 1 ):
        #stimuli
        present_color = random.choice(colors)
        present_word =random.choice(words)
        fixation = stimuli.FixCross()

        if ((present_word == 'red' and present_color == C_RED)  
            or (present_word == 'green' and present_color == C_GREEN)
            or (present_word == 'blue' and present_color == C_BLUE)
            or (present_word == 'orange' and present_color == C_ORANGE)):
            trial_type = 'match'

        else: 
            trial_type = 'mismatch'

            
        #single trial
        fixation.present(clear = True, update = True)
        exp.clock.wait(500)
        stroop = stimuli.TextLine(text = present_word, text_colour = present_color)
        stroop.present(clear=True, update = True)
        key, rt = exp.keyboard.wait(keys =[K_s, K_k])
        Accuracy = 0
        #feedback
        if (key == K_s and trial_type == 'match') or (key == K_k and trial_type == 'mismatch'):
            Accuracy +=1
            feedback = 'Great job'
        else: 
            feedback = 'Check it more carefully'
            Accuracy =0

        exp.screen.clear()

        show_feedback = stimuli.TextLine(text = feedback)
        show_feedback.present(clear = True, update = True)
        exp.clock.wait(1000)
        exp.data.add([block, trial, trial_type, present_word, present_color, key, Accuracy])
