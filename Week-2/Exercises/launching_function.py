from expyriment import design, control, stimuli # import packadge

def horizontal_launching_event(temporal_gap = 0, spatial_gap = 0, g_r_speed_ratio = 1):

    size = (50, 50) # squere's default size
    steps = 70 # number of steps
    wait = 10

    left_start = -400 # position of starting point of red square
    left_end = -50 # position of ending point of red square
    right_start = left_end + 20 + spatial_gap # position of starting point of green square
    right_end = 400 # position of ending point of green square

    left_square = stimuli.Rectangle(size=size, colour=(255,0,0), position=(left_start,0))
    right_square = stimuli.Rectangle(size=size, colour=(0,255,0), position=(right_start,0))
    
    left_square.present(clear=True, update=False) # present the left square
    right_square.present(clear=False, update=True)
    exp.clock.wait(500)

    left_dx = (left_end - left_start) / steps # calculate the single  movement for red square
    right_dx = ((right_end - right_start) / steps) *g_r_speed_ratio # calculate the single  movement for red square
    right_start_time = None


    for i in range(steps):
        # Move red until it reaches left_end
        if i < steps //2:
            left_square.move((left_dx,0))
        else:
            if right_start_time is None:
                right_start_time = exp.clock.time
            if temporal_gap == 0 or (exp.clock.time - right_start_time >= temporal_gap):
                right_square.move((right_dx,0))
        left_square.present(clear=True, update=False) # present the left square
        right_square.present(clear=False, update=True) # present the right square
        exp.clock.wait(10)


control.set_develop_mode()
exp = design.Experiment(name='Horizontal launching function')
control.initialize(exp)
control.start(subject_id=1)

# Michottean launching
horizontal_launching_event(temporal_gap=0, spatial_gap=0, g_r_speed_ratio=1)

# temporal gap
horizontal_launching_event(temporal_gap=200, spatial_gap=0, g_r_speed_ratio=1)

# spatial gap
horizontal_launching_event(temporal_gap=0, spatial_gap=50, g_r_speed_ratio=1)

# triggering (green moves faster)
horizontal_launching_event(temporal_gap=0, spatial_gap=0, g_r_speed_ratio=3)
