import expyriment
from expyriment import design, control, stimuli
from expyriment.misc.constants import C_BLACK, C_GREEN, K_SPACE, K_LEFT, K_RIGHT
import random
import math
import csv
import os

# ==============================
# PARAMETERS
# ==============================
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = C_BLACK

PATTERN_WIDTH = 160
PATTERN_HEIGHT = 240
PATTERN_COLOR = (102, 102, 102)

DOT_DIAMETER = 12
DOT_COLOR = (0, 0, 0)
MIN_DOT_DISTANCE = 42
MIN_DOT_BOUNDARY_DISTANCE = 10

LINE_WIDTH = 2
LINE_COLOR = (0, 0, 0)
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12

NUM_REFERENCE_DOTS = 12
NUM_LINES = 4
TEST_DOT_NUMBERS = [9,10,11,12,13,14,15]
CONNECTEDNESS_LEVELS = [0,1,2]
PATTERNS_PER_CONDITION = 8

STIMULUS_DURATION = 200
HEMIFIELD_OFFSET = 200

NUM_BLOCKS = 1  # for testing
TRIALS_PER_HALF_BLOCK = 168  # 21 conditions x 8

DATA_FILENAME = "experiment_data.csv"

# ==============================
# HELPERS
# ==============================
def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def point_to_segment_distance(point, seg_start, seg_end):
    px, py = point
    x1, y1 = seg_start
    x2, y2 = seg_end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return distance(point, seg_start)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy)/(dx*dx + dy*dy)))
    closest_x = x1 + t*dx
    closest_y = y1 + t*dy
    return distance(point, (closest_x, closest_y))

def lines_intersect(l1, l2):
    (x1,y1),(x2,y2) = l1
    (x3,y3),(x4,y4) = l2
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom)<1e-10:
        return False
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4))/denom
    u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3))/denom
    return 0 < t < 1 and 0 < u < 1

# ==============================
# DOT & LINE GENERATION
# ==============================
def generate_dots(n_dots):
    dots = []
    attempts_max = 10000
    for _ in range(n_dots):
        for _ in range(attempts_max):
            x = random.randint(-PATTERN_WIDTH//2+MIN_DOT_BOUNDARY_DISTANCE,
                               PATTERN_WIDTH//2-MIN_DOT_BOUNDARY_DISTANCE)
            y = random.randint(-PATTERN_HEIGHT//2+MIN_DOT_BOUNDARY_DISTANCE,
                               PATTERN_HEIGHT//2-MIN_DOT_BOUNDARY_DISTANCE)
            if all(distance((x,y), d)>=MIN_DOT_DISTANCE for d in dots):
                dots.append((x,y))
                break
        else:
            raise RuntimeError("Cannot place dot")
    return dots

def generate_free_lines(n_lines, dots=[], existing_lines=[]):
    lines = list(existing_lines)
    for _ in range(n_lines):
        for attempt in range(1000):
            x1 = random.randint(-PATTERN_WIDTH//2, PATTERN_WIDTH//2)
            y1 = random.randint(-PATTERN_HEIGHT//2, PATTERN_HEIGHT//2)
            angle = random.uniform(0,2*math.pi)
            length = random.uniform(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            x2 = x1 + length*math.cos(angle)
            y2 = y1 + length*math.sin(angle)
            if not (-PATTERN_WIDTH//2 <= x2 <= PATTERN_WIDTH//2 and -PATTERN_HEIGHT//2 <= y2 <= PATTERN_HEIGHT//2):
                continue
            if any(point_to_segment_distance(d,(x1,y1),(x2,y2)) < MIN_LINE_DOT_DISTANCE for d in dots):
                continue
            if any(lines_intersect(((x1,y1),(x2,y2)),l) for l in lines):
                continue
            lines.append(((x1,y1),(x2,y2)))
            break
        else:
            raise RuntimeError("Cannot place line")
    return lines

def generate_connecting_lines(dots, n_connection, existing_lines=[]):
    lines = list(existing_lines)
    connected_pairs = []
    available_dots = list(range(len(dots)))
    for _ in range(n_connection):
        if len(available_dots)<2:
            break
        for _ in range(1000):
            i1,i2 = random.sample(available_dots,2)
            p1,p2 = dots[i1], dots[i2]
            d = distance(p1,p2)
            if not(MIN_LINE_LENGTH<=d<=MAX_LINE_LENGTH):
                continue
            if any(lines_intersect((p1,p2),l) for l in lines):
                continue
            lines.append((p1,p2))
            connected_pairs.append((i1,i2))
            available_dots.remove(i1)
            available_dots.remove(i2)
            break
    return lines, connected_pairs

# ==============================
# PATTERN CLASS
# ==============================
class DotPattern:
    def __init__(self, dots, n_connection=0):
        self.dots = dots
        self.n_connection = n_connection
        self.lines = []
        self.connected_pairs = []

    def generate_lines(self):
        if self.n_connection>0:
            self.lines, self.connected_pairs = generate_connecting_lines(self.dots, self.n_connection)
        free_lines_needed = NUM_LINES - len(self.lines)
        if free_lines_needed>0:
            self.lines = generate_free_lines(free_lines_needed, self.dots, self.lines)

# ==============================
# REFERENCE & TEST GENERATION
# ==============================
def generate_reference_patterns():
    ref_patterns = []
    for _ in range(TRIALS_PER_HALF_BLOCK):
        dots = generate_dots(NUM_REFERENCE_DOTS)
        pattern = DotPattern(dots, n_connection=0)
        pattern.generate_lines()
        ref_patterns.append(pattern)
    return ref_patterns

def generate_test_patterns(ref_patterns):
    test_patterns = []
    for pattern in ref_patterns:
        for connectedness in CONNECTEDNESS_LEVELS:
            for n_dots in TEST_DOT_NUMBERS:
                # Copy reference dots
                test_dots = list(pattern.dots)
                if n_dots>NUM_REFERENCE_DOTS:
                    # add extra dots
                    extra = generate_dots(n_dots-NUM_REFERENCE_DOTS)
                    test_dots.extend(extra)
                elif n_dots<NUM_REFERENCE_DOTS:
                    # remove dots randomly
                    test_dots = random.sample(test_dots,n_dots)
                test_pattern = DotPattern(test_dots, connectedness)
                test_pattern.generate_lines()
                test_patterns.append(test_pattern)
    return test_patterns

# ==============================
# DISPLAY & TRIAL
# ==============================
def create_pattern_stimulus(pattern, offset_x):
    canvas = stimuli.Canvas((PATTERN_WIDTH,PATTERN_HEIGHT), colour=PATTERN_COLOR, position=(offset_x,0))
    for d in pattern.dots:
        stimuli.Circle(DOT_DIAMETER/2, colour=DOT_COLOR, position=d).plot(canvas)
    for l in pattern.lines:
        stimuli.Line(l[0], l[1], LINE_WIDTH, LINE_COLOR).plot(canvas)
    return canvas

def run_trial(exp, ref_pattern, test_pattern, test_on_left=True):
    fixation = stimuli.FixCross(size=(20,20),colour=C_GREEN,line_width=2)
    fixation.present()
    exp.clock.wait(200)

    left_pattern = test_pattern if test_on_left else ref_pattern
    right_pattern = ref_pattern if test_on_left else test_pattern

    left_canvas = create_pattern_stimulus(left_pattern, -HEMIFIELD_OFFSET)
    right_canvas = create_pattern_stimulus(right_pattern, HEMIFIELD_OFFSET)

    display = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    left_canvas.plot(display)
    right_canvas.plot(display)
    display.present()
    exp.clock.wait(STIMULUS_DURATION)

    blank = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    blank.present()
    key, rt = exp.keyboard.wait([K_LEFT,K_RIGHT])

    choice_side = "left" if key==K_LEFT else "right"
    test_side = "left" if test_on_left else "right"
    chose_test = (choice_side==test_side)
    return choice_side, test_side, chose_test, rt

# ==============================
# EXPERIMENT
# ==============================
def run_experiment():
    exp = design.Experiment("Connectedness_Numerosity")
    control.initialize(exp)
    control.start(skip_ready_screen=True)

    ref_patterns = generate_reference_patterns()
    test_patterns = generate_test_patterns(ref_patterns)

    data_file = open(DATA_FILENAME,"w",newline="")
    writer = csv.writer(data_file)
    writer.writerow(["trial","num_dots","connectedness","test_on_left","choice","test_side","chose_test","rt"])

    trial_num=0
    for ref, test in zip(ref_patterns, test_patterns[:len(ref_patterns)]):
        test_on_left = random.choice([True,False])
        choice, test_side, chose_test, rt = run_trial(exp, ref, test, test_on_left)
        trial_num+=1
        writer.writerow([trial_num,len(test.dots),test.n_connection,test_on_left,choice,test_side,chose_test,rt])
    data_file.close()
    control.end()

# ==============================
# RUN
# ==============================
if __name__=="__main__":
    run_experiment()
