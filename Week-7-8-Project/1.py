""" 
  Saves CSV with headers:
  participant_id, timestamp, block, half, trial_in_block, num_dots, connectedness,
  test_on_left, choice_side, test_side, chose_test (1/0), rt_ms, pattern_signature
"""

import expyriment
from expyriment import design, control, stimuli
from expyriment.misc.constants import C_BLACK, C_GREEN, K_SPACE, K_LEFT, K_RIGHT
import random
import math
import csv
import time
import os
from datetime import datetime
import itertools

# -----------------------
# PARAMETERS / CONSTANTS
# -----------------------
SCREEN_SIZE = (1024, 768)
BACKGROUND_COLOR = (0, 0, 0)

# Pattern geometry (main script values, adjusted as requested)
PATTERN_WIDTH = 160
PATTERN_HEIGHT = 240
PATTERN_COLOR = (102, 102, 102)

# Dot constraints
DOT_DIAMETER = 12
DOT_COLOR = (0, 0, 0)
MIN_DOT_DISTANCE = 42                  # must be >= 42 px apart
MIN_DOT_BOUNDARY_DISTANCE = 10         # must be >=10 px from edges

# Line constraints
LINE_WIDTH = 2
LINE_COLOR = (0, 0, 0)
MIN_LINE_LENGTH = 30
MAX_LINE_LENGTH = 60
MIN_LINE_DOT_DISTANCE = 12             # lines must be >=12 px from any dot (except endpoints for connecting lines)

# Experiment design
NUM_REFERENCE_DOTS = 12
NUM_LINES = 4
TEST_DOT_NUMBERS = [9,10,11,12,13,14,15]   # 7 levels
CONNECTEDNESS_LEVELS = [0,1,2]             # 0/1/2 connections
PATTERNS_PER_CONDITION = 8                 # 8 patterns per (connectedness x dot-number)
TRIALS_PER_HALF_BLOCK = 168                # 21 conditions x 8 reps
NUM_BLOCKS = 5
NUM_PRACTICE_TRIALS = 30
PRACTICE_TEST_DOTS = 9

# Timing
STIMULUS_DURATION = 200   # ms
MIN_ITI = 500
MAX_ITI = 1000

# Positioning
HEMIFIELD_OFFSET = 200

# -----------------------
# GEOMETRY HELPERS
# -----------------------
def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def lines_intersect(l1, l2):
    (x1,y1), (x2,y2) = l1
    (x3,y3), (x4,y4) = l2
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom) < 1e-10:
        return False
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
    u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / denom
    return 0 < t < 1 and 0 < u < 1

def point_to_segment_distance(point, a, b):
    px, py = point
    x1, y1 = a
    x2, y2 = b
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1)*dx + (py - y1)*dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    cx = x1 + t*dx
    cy = y1 + t*dy
    return math.hypot(px - cx, py - cy)

# -----------------------
# PATTERN SIGNATURE & MIRRORING (for uniqueness and CSV)
# -----------------------
def pattern_signature(pattern):
    # canonical signature: sorted integer-rounded dots and sorted lines
    dots_sig = tuple(sorted((int(round(x)), int(round(y))) for x,y in pattern['dots']))
    lines_sig = tuple(sorted(((int(round(l[0][0])),int(round(l[0][1]))),(int(round(l[1][0])),int(round(l[1][1])))) for l in pattern['lines']))
    return (dots_sig, lines_sig)

def mirror_pattern(pattern):
    # reflect x coordinate sign
    mirrored = {
        'dots': [(-x, y) for x,y in pattern['dots']],
        'lines': [((-l[0][0], l[0][1]), (-l[1][0], l[1][1])) for l in pattern['lines']],
        'pairs': [(b,a) for (a,b) in pattern.get('pairs', [])],  # pairs indices not used elsewhere
        'n_dots': pattern['n_dots'],
        'n_connection': pattern['n_connection']
    }
    return mirrored

# -----------------------
# DOT GENERATION (strict)
# -----------------------
def generate_dots(n_dots, max_attempts=20000):
    dots = []
    min_x = -PATTERN_WIDTH//2 + MIN_DOT_BOUNDARY_DISTANCE
    max_x = PATTERN_WIDTH//2 - MIN_DOT_BOUNDARY_DISTANCE
    min_y = -PATTERN_HEIGHT//2 + MIN_DOT_BOUNDARY_DISTANCE
    max_y = PATTERN_HEIGHT//2 - MIN_DOT_BOUNDARY_DISTANCE
    if min_x > max_x or min_y > max_y:
        raise RuntimeError("Pattern bounds incompatible with boundary constraints.")
    attempts_total = 0
    for i in range(n_dots):
        placed = False
        while not placed and attempts_total < max_attempts:
            attempts_total += 1
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            if all(distance((x,y), d) >= MIN_DOT_DISTANCE for d in dots):
                dots.append((x,y))
                placed = True
        if not placed:
            raise RuntimeError(f"Could not place dot {i+1}/{n_dots} after {max_attempts} attempts.")
    return dots

# -----------------------
# FREE LINES GENERATION
# -----------------------
def generate_free_lines(n_lines, dots, existing_lines=None, max_attempts_per_line=2000):
    if existing_lines is None:
        existing_lines = []
    lines = list(existing_lines)
    for _ in range(n_lines):
        placed = False
        for attempt in range(max_attempts_per_line):
            x1 = random.randint(-PATTERN_WIDTH//2, PATTERN_WIDTH//2)
            y1 = random.randint(-PATTERN_HEIGHT//2, PATTERN_HEIGHT//2)
            angle = random.uniform(0, 2*math.pi)
            length = random.uniform(MIN_LINE_LENGTH, MAX_LINE_LENGTH)
            x2 = x1 + length*math.cos(angle)
            y2 = y1 + length*math.sin(angle)
            # bounds check for endpoint
            if not (-PATTERN_WIDTH//2 <= x2 <= PATTERN_WIDTH//2 and -PATTERN_HEIGHT//2 <= y2 <= PATTERN_HEIGHT//2):
                continue
            new_line = ((x1,y1),(x2,y2))
            # not intersect existing
            if any(lines_intersect(new_line, l) for l in lines):
                continue
            # must be >= MIN_LINE_DOT_DISTANCE from all dots
            if any(point_to_segment_distance(d, new_line[0], new_line[1]) < MIN_LINE_DOT_DISTANCE for d in dots):
                continue
            lines.append(new_line)
            placed = True
            break
        if not placed:
            raise RuntimeError("Could not place a free line after many attempts.")
    return lines

# -----------------------
# CONNECTING LINES GENERATION (connect centers)
# -----------------------
def generate_connecting_lines_from_dots(dots, n_connection, existing_lines=None, max_attempts=2000):
    if existing_lines is None:
        existing_lines = []
    connecting_lines = list(existing_lines)
    connected_pairs = []
    available = set(range(len(dots)))
    for _ in range(n_connection):
        placed = False
        attempts = 0
        while attempts < max_attempts and not placed:
            attempts += 1
            if len(available) < 2:
                break
            i1, i2 = random.sample(list(available), 2)
            p1 = dots[i1]; p2 = dots[i2]
            d = distance(p1,p2)
            if not (MIN_LINE_LENGTH <= d <= MAX_LINE_LENGTH):
                continue
            new_line = (p1, p2)
            if any(lines_intersect(new_line, l) for l in connecting_lines):
                continue
            # ensure new_line distance to other dots (excluding endpoints)
            others = set(range(len(dots))) - {i1, i2}
            if any(point_to_segment_distance(dots[i], p1, p2) < MIN_LINE_DOT_DISTANCE for i in others):
                continue
            # accept
            connecting_lines.append(new_line)
            connected_pairs.append((i1, i2))
            available.remove(i1); available.remove(i2)
            placed = True
        if not placed:
            # fail gracefully (return what we have); caller must handle insufficient connections
            break
    return connecting_lines, connected_pairs

# -----------------------
# BUILDING PATTERNS: reference/test pools
# - Reference patterns are 0-connected with NUM_REFERENCE_DOTS
# - Test patterns: for each n_dots and n_connection, produce PATTERNS_PER_CONDITION
#   when n_connection>0: reuse base 0-connected dots to create connecting lines (replace free lines)
# -----------------------
def generate_reference_pool(n_patterns=TRIALS_PER_HALF_BLOCK):
    pool = []
    seen = set()
    attempts = 0
    while len(pool) < n_patterns:
        attempts += 1
        if attempts > n_patterns * 2000:
            raise RuntimeError("Failed to build enough unique reference patterns: loosen constraints.")
        try:
            dots = generate_dots(NUM_REFERENCE_DOTS)
            lines = generate_free_lines(NUM_LINES, dots)
        except RuntimeError:
            continue
        p = {'dots': dots, 'lines': lines, 'pairs': [], 'n_dots': NUM_REFERENCE_DOTS, 'n_connection': 0}
        sig = pattern_signature(p)
        if sig in seen:
            continue
        seen.add(sig); pool.append(p)
    return pool

def replace_free_lines_with_connecting(dots, free_lines, n_connections):
    """
    Try to replace exactly n_connections free lines by n_connections connecting lines
    between dot centers while preserving constraints.
    Returns final_lines, connected_pairs on success, raises RuntimeError on failure.
    """
    # We'll attempt randomized searches
    max_outer = 2000
    for outer in range(max_outer):
        copy_free = free_lines.copy()
        connected = []
        pairs = []
        used_dots = set()
        ok = True
        for c in range(n_connections):
            # try to find a suitable pair that is not yet used
            found = False
            indices = list(range(len(dots)))
            random.shuffle(indices)
            for i1 in indices:
                if i1 in used_dots: continue
                for i2 in indices:
                    if i2 == i1 or i2 in used_dots: continue
                    p1 = dots[i1]; p2 = dots[i2]
                    d = distance(p1,p2)
                    if not (MIN_LINE_LENGTH <= d <= MAX_LINE_LENGTH):
                        continue
                    cand_line = (p1,p2)
                    # must not intersect existing connecting lines or remaining free lines
                    if any(lines_intersect(cand_line, l) for l in connected + copy_free):
                        continue
                    # must be >= MIN_LINE_DOT_DISTANCE from other dots
                    others = set(range(len(dots))) - {i1,i2}
                    if any(point_to_segment_distance(dots[o], p1, p2) < MIN_LINE_DOT_DISTANCE for o in others):
                        continue
                    # accept
                    connected.append(cand_line)
                    pairs.append((i1,i2))
                    used_dots.add(i1); used_dots.add(i2)
                    found = True
                    break
                if found: break
            if not found:
                ok = False
                break
            # remove a random free line to represent the "replacement"
            if copy_free:
                copy_free.pop(random.randrange(len(copy_free)))
            else:
                ok = False
                break
        if not ok:
            continue
        # final validation: connected + remaining free should not intersect mutually
        final_lines = copy_free + connected
        valid = True
        for a,b in itertools.combinations(final_lines, 2):
            if lines_intersect(a,b):
                valid = False; break
        if not valid:
            continue
        # ensure non-connecting lines are >= MIN_LINE_DOT_DISTANCE from dots
        for ln in final_lines:
            for d in dots:
                if ln in connected and (d == ln[0] or d == ln[1]):
                    continue
                if point_to_segment_distance(d, ln[0], ln[1]) < MIN_LINE_DOT_DISTANCE:
                    valid = False; break
            if not valid:
                break
        if not valid:
            continue
        # success
        return final_lines, pairs
    raise RuntimeError("Failed to replace free lines with connecting lines after many attempts.")

def generate_test_pool():
    """
    Create test patterns for all conditions.
    Approach:
      - For each n_dots, create a small pool of distinct 0-connected base configurations (NUM_LINES free lines)
      - For 1- and 2-connected conditions derive from those bases reusing the exact dots
      - Produce mirrored versions too to increase distinctness
    """
    test_patterns = []
    # for each n_dots, create base pool of size >= PATTERNS_PER_CONDITION
    base_pool = {}
    for n in TEST_DOT_NUMBERS:
        base_list = []
        seen = set()
        attempts = 0
        needed = max(8, PATTERNS_PER_CONDITION)   # create enough bases
        while len(base_list) < needed:
            attempts += 1
            if attempts > needed * 2000:
                raise RuntimeError(f"Failed generating base pool for {n} dots.")
            try:
                dots = generate_dots(n)
                free_lines = generate_free_lines(NUM_LINES, dots)
            except RuntimeError:
                continue
            p = {'dots': dots, 'lines': free_lines, 'pairs': [], 'n_dots': n, 'n_connection': 0}
            sig = pattern_signature(p)
            if sig in seen:
                continue
            seen.add(sig); base_list.append(p)
        base_pool[n] = base_list

    # Now derive patterns for each connectedness/n_dots
    for n_conn in CONNECTEDNESS_LEVELS:
        for n in TEST_DOT_NUMBERS:
            created = 0
            base_idx = 0
            while created < PATTERNS_PER_CONDITION:
                base = base_pool[n][base_idx % len(base_pool[n])]
                base_idx += 1
                dots = [tuple(pt) for pt in base['dots']]                 # reuse exact dots
                free_lines = [tuple(((l[0][0],l[0][1]),(l[1][0],l[1][1]))) for l in base['lines']]
                if n_conn == 0:
                    pattern = {'dots': dots, 'lines': free_lines.copy(), 'pairs': [], 'n_dots': n, 'n_connection': 0}
                    sig = pattern_signature(pattern)
                    # ensure uniqueness
                    if not any(sig == pattern_signature(p) for p in test_patterns):
                        test_patterns.append(pattern); created += 1
                        # also add mirrored if possible and still under quota
                        if created < PATTERNS_PER_CONDITION:
                            mir = mirror_pattern(pattern)
                            msig = pattern_signature(mir)
                            if not any(msig == pattern_signature(p) for p in test_patterns):
                                test_patterns.append(mir); created += 1
                    continue
                # generate connecting lines derived from base dots
                try:
                    final_lines, pairs = replace_free_lines_with_connecting(dots, free_lines, n_conn)
                except RuntimeError:
                    # couldn't derive from this base; try next base
                    continue
                pattern = {'dots': dots, 'lines': final_lines, 'pairs': pairs, 'n_dots': n, 'n_connection': n_conn}
                sig = pattern_signature(pattern)
                if any(sig == pattern_signature(p) for p in test_patterns):
                    continue
                test_patterns.append(pattern); created += 1
                # add mirrored variant if space
                if created < PATTERNS_PER_CONDITION:
                    mir = mirror_pattern(pattern)
                    msig = pattern_signature(mir)
                    if not any(msig == pattern_signature(p) for p in test_patterns):
                        test_patterns.append(mir); created += 1
    random.shuffle(test_patterns)
    return test_patterns

# -----------------------
# CREATE & PRELOAD CANVASES
# -----------------------
def create_pattern_canvas(pattern, offset_x):
    # Create a Canvas sized to pattern with elements plotted (coordinates centered at 0,0)
    canvas = stimuli.Canvas(size=(PATTERN_WIDTH, PATTERN_HEIGHT), colour=PATTERN_COLOR, position=(offset_x,0))
    for (x,y) in pattern['dots']:
        dot = stimuli.Circle(radius=DOT_DIAMETER/2, colour=DOT_COLOR, position=(x,y))
        dot.plot(canvas)
    for ((x1,y1),(x2,y2)) in pattern['lines']:
        line = stimuli.Line(start_point=(x1,y1), end_point=(x2,y2), line_width=LINE_WIDTH, colour=LINE_COLOR)
        line.plot(canvas)
    try:
        canvas.preload()
    except Exception:
        pass
    return canvas

# -----------------------
# TRIAL/EXPERIMENT HELPERS
# -----------------------
def create_trial_list(reference_patterns, test_patterns, block_num):
    # pick first TRIALS_PER_HALF_BLOCK patterns from each pool (we assume pools >= TRIALS_PER_HALF_BLOCK)
    indices = list(range(TRIALS_PER_HALF_BLOCK))
    random.shuffle(indices)
    trials = []
    for i in indices:
        ref = reference_patterns[i]
        test = test_patterns[i]
        test_on_left = random.choice([True, False])
        trial = {
            'block': block_num,
            'half': 1,
            'trial_in_half': i+1,
            'reference_pattern': ref,
            'test_pattern': test,
            'test_on_left': test_on_left,
            'num_dots': test['n_dots'],
            'connectedness': test['n_connection'],
            'is_practice': False,
            'pattern_sig': pattern_signature(test)
        }
        trials.append(trial)
    # second half: same trials with reversed positions
    second = []
    for t in trials:
        nt = t.copy()
        nt['half'] = 2
        nt['test_on_left'] = not t['test_on_left']
        second.append(nt)
    full = trials + second
    random.shuffle(full)
    # enumerate trial numbers within block
    for idx, t in enumerate(full, start=1):
        t['trial_number_in_block'] = idx
    return full

def create_practice_trials():
    trials = []
    for i in range(NUM_PRACTICE_TRIALS):
        test_dots = generate_dots(PRACTICE_TEST_DOTS)
        test_lines = generate_free_lines(NUM_LINES, test_dots)
        test_pattern = {'dots': test_dots, 'lines': test_lines, 'pairs': [], 'n_dots': PRACTICE_TEST_DOTS, 'n_connection': 0}
        ref_pattern = generate_reference_pattern()
        trial = {
            'block': 0, 'half': 0, 'trial_in_half': i+1,
            'reference_pattern': ref_pattern, 'test_pattern': test_pattern,
            'test_on_left': random.choice([True, False]), 'num_dots': PRACTICE_TEST_DOTS,
            'connectedness': 0, 'is_practice': True, 'pattern_sig': pattern_signature(test_pattern)
        }
        trials.append(trial)
    return trials

def generate_reference_pattern():
    # wrapper to generate a single 0-connected reference pattern
    while True:
        try:
            dots = generate_dots(NUM_REFERENCE_DOTS)
            lines = generate_free_lines(NUM_LINES, dots)
            return {'dots': dots, 'lines': lines, 'pairs': [], 'n_dots': NUM_REFERENCE_DOTS, 'n_connection': 0}
        except RuntimeError:
            continue

# -----------------------
# PRESENTATION & TRIAL EXECUTION
# -----------------------
def present_pair_and_get_response(exp, left_canvas, right_canvas, fixation_cross):
    # fixation -> display -> response
    fixation_cross.present()
    exp.clock.wait(300)
    screen = stimuli.BlankScreen(colour=BACKGROUND_COLOR)
    left_canvas.plot(screen)
    right_canvas.plot(screen)
    screen.present()
    exp.clock.wait(STIMULUS_DURATION)
    stimuli.BlankScreen(colour=BACKGROUND_COLOR).present()
    key, rt = exp.keyboard.wait([K_LEFT, K_RIGHT])
    return key, rt

# -----------------------
# CSV SAVING
# -----------------------
def write_csv(filename, rows, headers):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

# -----------------------
# MAIN RUN
# -----------------------
def run_experiment(participant_id=None):
    # exp setup
    exp = design.Experiment(name="Connectedness_Numerosity_Checked")
    control.initialize(exp)
    control.set_develop_mode(False)

    # data header
    headers = ['participant_id','timestamp','block','half','trial_in_block','trial_number_in_block',
               'num_dots','connectedness','test_on_left','choice_side','test_side','chose_test','rt_ms','pattern_signature']

    # generate patterns (may take time)
    print("Generating patterns (may take a minute)...")
    reference_pool = generate_reference_pool()
    test_pool = generate_test_pool()
    print("Pattern generation done.")

    # preload canvases for first half-block
    preload = {}
    preload_count = min(TRIALS_PER_HALF_BLOCK, len(test_pool), len(reference_pool))
    for i in range(preload_count):
        r = reference_pool[i]; t = test_pool[i]
        for pat, side in [(r,'ref'), (t,'test')]:
            sig = pattern_signature(pat)
            # create L and R canvas
            keyL = (sig, 'L'); keyR = (sig, 'R')
            if keyL not in preload:
                preload[keyL] = create_pattern_canvas(pat, -HEMIFIELD_OFFSET)
                preload[keyR] = create_pattern_canvas(pat, HEMIFIELD_OFFSET)

    fixation = stimuli.FixCross(size=(20,20), colour=C_GREEN, line_width=2)
    fixation.preload()

    # Start experiment
    control.start(skip_ready_screen=True)

    # instructions
    instructions = stimuli.TextScreen("Numerosity Judgment Task",
                                     text="""Two patterns will flash briefly (left & right).
Decide which pattern has MORE dots.
Press LEFT arrow if LEFT pattern has more dots.
Press RIGHT arrow if RIGHT pattern has more dots.
Focus on the green cross.
Practice first, then main experiment.
Press SPACE to start.""")
    instructions.present()
    exp.keyboard.wait(K_SPACE)

    # practice
    practice_trials = create_practice_trials()
    stimuli.TextScreen("Practice", "Practice trials. Press SPACE to start.").present()
    exp.keyboard.wait(K_SPACE)
    data_rows = []
    ts_start = datetime.now().isoformat()
    for idx, t in enumerate(practice_trials, start=1):
        # build canvases
        left_pat = t['test_pattern'] if t['test_on_left'] else t['reference_pattern']
        right_pat = t['reference_pattern'] if t['test_on_left'] else t['test_pattern']
        left_key = (pattern_signature(left_pat),'L'); right_key = (pattern_signature(right_pat),'R')
        left_canvas = preload.get(left_key) or create_pattern_canvas(left_pat, -HEMIFIELD_OFFSET)
        right_canvas = preload.get(right_key) or create_pattern_canvas(right_pat, HEMIFIELD_OFFSET)
        key, rt = present_pair_and_get_response(exp, left_canvas, right_canvas, fixation)
        choice_side = "left" if key == K_LEFT else "right"
        test_side = "left" if t['test_on_left'] else "right"
        chose_test = int(choice_side == test_side)
        row = [
            participant_id or '',
            datetime.now().isoformat(),
            t['block'], t['half'], t['trial_in_half'], idx,
            t['num_dots'], t['connectedness'],
            t['test_on_left'],
            choice_side, test_side, chose_test, rt,
            str(t['pattern_sig'])
        ]
        data_rows.append(row)

    stimuli.TextScreen("Practice Complete", "Practice complete. Press SPACE to start main experiment.").present()
    exp.keyboard.wait(K_SPACE)

    # main blocks
    for block_num in range(1, NUM_BLOCKS+1):
        stimuli.TextScreen(f"Block {block_num} of {NUM_BLOCKS}", "Press SPACE to start").present()
        exp.keyboard.wait(K_SPACE)
        trials = create_trial_list(reference_pool, test_pool, block_num)
        # run trials
        for t in trials:
            # ITI
            exp.clock.wait(random.randint(MIN_ITI, MAX_ITI))
            # determine left/right patterns
            if t['test_on_left']:
                left_pat = t['test_pattern']; right_pat = t['reference_pattern']
            else:
                left_pat = t['reference_pattern']; right_pat = t['test_pattern']
            left_key = (pattern_signature(left_pat),'L'); right_key = (pattern_signature(right_pat),'R')
            left_canvas = preload.get(left_key) or create_pattern_canvas(left_pat, -HEMIFIELD_OFFSET)
            right_canvas = preload.get(right_key) or create_pattern_canvas(right_pat, HEMIFIELD_OFFSET)
            # present & response
            key, rt = present_pair_and_get_response(exp, left_canvas, right_canvas, fixation)
            choice_side = "left" if key == K_LEFT else "right"
            test_side = "left" if t['test_on_left'] else "right"
            chose_test = int(choice_side == test_side)
            row = [
                participant_id or '',
                datetime.now().isoformat(),
                t['block'], t['half'], t.get('trial_in_half', -1), t.get('trial_number_in_block', -1),
                t['num_dots'], t['connectedness'],
                t['test_on_left'],
                choice_side, test_side, chose_test, rt,
                str(t['pattern_sig'])
            ]
            data_rows.append(row)
        # break between blocks
        if block_num < NUM_BLOCKS:
            stimuli.TextScreen("Break", "Take a short break. Press SPACE to continue.").present()
            exp.keyboard.wait(K_SPACE)

    # end
    stimuli.TextScreen("Complete", "Thank you for participating.").present()
    exp.clock.wait(1500)
    control.end()

    # write CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"connectedness_data_{participant_id or 'p'}_{timestamp}.csv"
    write_csv(fname, data_rows, headers)
    print(f"Saved CSV to: {os.path.abspath(fname)}")
    return fname

# -----------------------
# RUN as script
# -----------------------
if __name__ == "__main__":
    # optional participant id prompt (simple)
    pid = input("Participant ID (or press Enter to leave blank): ").strip()
    try:
        csv_file = run_experiment(participant_id=pid if pid else None)
        print("Experiment finished. Data saved to:", csv_file)
    except Exception as e:
        print("ERROR during experiment run:", str(e))
        raise
