import expyriment
from expyriment import design, control, stimuli
from expyriment.misc.constants import C_BLACK, C_GREEN, K_SPACE, K_LEFT, K_RIGHT
import random
import numpy as np
import math

# -----------------------
# DISPLAY & STIMULUS CONSTANTS
# -----------------------
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)

PATTERN_WIDTH = 240
PATTERN_HEIGHT = 320
PATTERN_COLOR = (102, 102, 102)
PATTERN_OFFSET_X = 300

DOT_DIAMETER = 12
DOT_COLOR = (0, 0, 0)
MIN_DOT_DISTANCE = 42
MIN_DOT_BOUNDARY_DISTANCE = 10

LINE_WIDTH = 2
LINE_COLOR = (0, 0, 0)
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12

STIMULUS_DURATION = 200
MIN_ITI = 500
MAX_ITI = 1000

NUM_REFERENCE_DOTS = 12
NUM_LINES = 4
TEST_DOT_NUMBERS = [9, 10, 11, 12, 13, 14, 15]
CONNECTEDNESS_LEVELS = [0, 1, 2]
PATTERNS_PER_CONDITION = 8

NUM_BLOCKS = 5
TRIALS_PER_HALF_BLOCK = 168

NUM_PRACTICE_TRIALS = 30
PRACTICE_TEST_DOTS = 9

HEMIFIELD_OFFSET = 200

# -----------------------
# 🔁 Reproducibility
# -----------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
print(f"[INFO] Random seed set to {SEED} for reproducibility.")

# -----------------------
# Utility / geometry functions
# -----------------------
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def lines_intersect(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return False

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    return 0 < t < 1 and 0 < u < 1

def point_to_segment_distance(point, seg_start, seg_end):
    px, py = point
    x1, y1 = seg_start
    x2, y2 = seg_end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)

# -----------------------
# Pattern generation
# -----------------------
def generate_dots(n_dots):
    dots = []
    max_attempts = 10000
    for i in range(n_dots):
        for attempt in range(max_attempts):
            x = random.randint(-PATTERN_WIDTH // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                                PATTERN_WIDTH // 2 - MIN_DOT_BOUNDARY_DISTANCE)
            y = random.randint(-PATTERN_HEIGHT // 2 + MIN_DOT_BOUNDARY_DISTANCE,
                                PATTERN_HEIGHT // 2 - MIN_DOT_BOUNDARY_DISTANCE)
            if all(distance((x, y), d) >= MIN_DOT_DISTANCE for d in dots):
                dots.append((x, y))
                break
        else:
            raise RuntimeError(f'Could not place dot {i + 1}')
    return dots

def generate_free_lines(n_line, dots, existing_lines=None):
    if existing_lines is None:
        existing_lines = []
    lines = list(existing_lines)
    for _ in range(n_line):
        for attempt in range(1000):
            x1 = random.randint(-PATTERN_WIDTH // 2, PATTERN_WIDTH // 2)
            y1 = random.randint(-PATTERN_HEIGHT // 2, PATTERN_HEIGHT // 2)
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            x2 = x1 + length * math.cos(angle)
            y2 = y1 + length * math.sin(angle)

            if not (-PATTERN_WIDTH // 2 <= x2 <= PATTERN_WIDTH // 2 and 
                    -PATTERN_HEIGHT // 2 <= y2 <= PATTERN_HEIGHT // 2):
                continue

            if any(point_to_segment_distance(d, (x1, y1), (x2, y2)) < MIN_LINE_DOT_DISTANCE for d in dots):
                continue

            if any(lines_intersect(((x1, y1), (x2, y2)), l) for l in lines):
                continue

            lines.append(((x1, y1), (x2, y2)))
            break
        else:
            raise RuntimeError('Could not place a line')
    return lines

def generate_connecting_lines(dots, n_connection, existing_lines=None):
    if existing_lines is None:
        existing_lines = []
    connecting_lines = list(existing_lines)
    connected_pairs = []
    available_dots = list(range(len(dots)))

    for _ in range(n_connection):
        if len(available_dots) < 2:
            break
        for attempt in range(1000):
            i1, i2 = random.sample(available_dots, 2)
            p1, p2 = dots[i1], dots[i2]
            d = distance(p1, p2)
            if not (MIN_LINE_LENGTH <= d <= MAX_LINE_LENGTH):
                continue
            if any(lines_intersect((p1, p2), l) for l in connecting_lines):
                continue
            if any(point_to_segment_distance(dpt, p1, p2) < MIN_LINE_DOT_DISTANCE for dpt in dots):
                continue
            connecting_lines.append((p1, p2))
            connected_pairs.append((i1, i2))
            available_dots.remove(i1)
            available_dots.remove(i2)
            break
        else:
            print('Warning: Could not place a connecting line')
    return connecting_lines, connected_pairs

# -----------------------
# Reference and Test share same dots
# -----------------------
def generate_reference_pattern():
    dots = generate_dots(NUM_REFERENCE_DOTS)
    lines = generate_free_lines(NUM_LINES, dots)
    return {'dots': dots, 'lines': lines, 'pairs': [], 'n_dots': NUM_REFERENCE_DOTS, 'n_connection': 0}

def generate_test_pattern_from_reference(reference_pattern, n_connection):
    dots = reference_pattern['dots'][:]  # same dots
    lines = []
    pairs = []
    if n_connection > 0:
        lines, pairs = generate_connecting_lines(dots, n_connection)
    n_free = NUM_LINES - len(lines)
    if n_free > 0:
        lines = generate_free_lines(n_free, dots, existing_lines=lines)
    return {'dots': dots, 'lines': lines, 'pairs': pairs, 'n_dots': len(dots), 'n_connection': n_connection}

# -----------------------
# Generate all patterns
# -----------------------
def generate_all_patterns():
    reference_patterns = [generate_reference_pattern() for _ in range(TRIALS_PER_HALF_BLOCK)]
    test_patterns = []
    for ref in reference_patterns:
        for conn in CONNECTEDNESS_LEVELS:
            test_patterns.append(generate_test_pattern_from_reference(ref, conn))
    random.shuffle(reference_patterns)
    random.shuffle(test_patterns)
    return reference_patterns, test_patterns

# -----------------------
# Trial creation
# -----------------------
def create_trial_list(reference_patterns, test_patterns, block_num):
    trials = []
    number_of_trials = TRIALS_PER_HALF_BLOCK
    for i in range(number_of_trials):
        ref_pattern = reference_patterns[i]
        test_pattern = test_patterns[i]
        test_on_left = random.choice([True, False])
        trial_info = {
            'block': block_num,
            'half': 1,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': test_pattern['n_dots'],
            'connectedness': test_pattern['n_connection'],
            'is_practice': False
        }
        trials.append(trial_info)
    return trials

def run_experiment():
    # ---------------------------------------------------
    # 1. Initialize experiment
    # ---------------------------------------------------
    exp = design.Experiment(name="Connectedness Affects Dot Numerosity Judgment")
    control.initialize(exp)
    control.set_develop_mode(False)
    control.start(skip_ready_screen=True)

    # Background
    exp.screen.clear(BACKGROUND_COLOR)
    exp.screen.update()

    # ---------------------------------------------------
    # 2. Instructions
    # ---------------------------------------------------
    instructions = stimuli.TextScreen(
        "Instructions",
        "In each trial, two patterns of dots will briefly appear on the screen.\n\n"
        "Your task: decide which pattern contains MORE dots.\n\n"
        "Press LEFT if the left pattern has more dots.\n"
        "Press RIGHT if the right pattern has more dots.\n\n"
        "There is no feedback. Try to respond as accurately as possible.\n\n"
        "Press SPACE to start the practice trials.",
        text_size=28,
        text_colour=(255, 255, 255)
    )
    instructions.present()
    exp.keyboard.wait(K_SPACE)

    # ---------------------------------------------------
    # 3. Practice trials
    # ---------------------------------------------------
    practice_trials = []
    for i in range(NUM_PRACTICE_TRIALS):
        ref_pattern = generate_reference_pattern()
        test_pattern = generate_test_pattern_from_reference(ref_pattern, 0)
        test_on_left = random.choice([True, False])
        trial_info = {
            'block': 0,
            'half': 0,
            'reference_pattern': ref_pattern,
            'test_pattern': test_pattern,
            'test_on_left': test_on_left,
            'num_dots': PRACTICE_TEST_DOTS,
            'connectedness': 0,
            'is_practice': True
        }
        practice_trials.append(trial_info)

    # Run practice
    for trial in practice_trials:
        run_single_trial(trial, exp)

    rest_screen = stimuli.TextScreen(
        "End of Practice",
        "Good job!\n\nThe main experiment will now begin.\n\n"
        "Press SPACE when you are ready.",
        text_size=28,
        text_colour=(255, 255, 255)
    )
    rest_screen.present()
    exp.keyboard.wait(K_SPACE)

    # ---------------------------------------------------
    # 4. Main experiment
    # ---------------------------------------------------
    for block in range(1, NUM_BLOCKS + 1):
        exp.screen.clear()
        exp.screen.update()
        msg = stimuli.TextScreen(
            f"Block {block}",
            "Get ready!\n\nPress SPACE to start.",
            text_size=28,
            text_colour=(255, 255, 255)
        )
        msg.present()
        exp.keyboard.wait(K_SPACE)

        # Generate patterns for this block
        reference_patterns, test_patterns = generate_all_patterns()

        # Create trial list (one “half” = randomized conditions)
        trials_half1 = create_trial_list(reference_patterns, test_patterns, block)

        # Second half = same trials but reversed sides
        trials_half2 = []
        for t in trials_half1:
            t2 = t.copy()
            t2['test_on_left'] = not t['test_on_left']
            t2['half'] = 2
            trials_half2.append(t2)

        block_trials = trials_half1 + trials_half2
        random.shuffle(block_trials)

        # Run all trials in this block
        for trial in block_trials:
            run_single_trial(trial, exp)

        # Short break between blocks
        if block < NUM_BLOCKS:
            rest_screen = stimuli.TextScreen(
                f"End of Block {block}",
                "Take a short break.\n\nPress SPACE when ready to continue.",
                text_size=28,
                text_colour=(255, 255, 255)
            )
            rest_screen.present()
            exp.keyboard.wait(K_SPACE)

    # ---------------------------------------------------
    # 5. End of experiment
    # ---------------------------------------------------
    end_screen = stimuli.TextScreen(
        "End of Experiment",
        "Thank you for participating!\n\nPress SPACE to exit.",
        text_size=28,
        text_colour=(255, 255, 255)
    )
    end_screen.present()
    exp.keyboard.wait(K_SPACE)
    control.end()


def create_pattern_stimulus(pattern):
    stim = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT), colour=(255, 255, 255))
    for (x, y) in pattern['dots']:
        dot = stimuli.Circle(radius=DOT_DIAMETER // 2, colour=DOT_COLOR)
        dot.plot(stim, (x + PATTERN_WIDTH // 2, y + PATTERN_HEIGHT // 2))
    for ((x1, y1), (x2, y2)) in pattern['lines']:
        line = stimuli.Line(start_position=(x1 + PATTERN_WIDTH // 2, y1 + PATTERN_HEIGHT // 2),
                            end_position=(x2 + PATTERN_WIDTH // 2, y2 + PATTERN_HEIGHT // 2),
                            colour=LINE_COLOR, line_width=LINE_WIDTH)
        line.plot(stim)
    return stim


if __name__ == "__main__":
    run_experiment()