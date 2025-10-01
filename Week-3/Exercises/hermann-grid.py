from expyriment import design, control, stimuli
import expyriment

def hermann(sq_size, sp_bt_sq, n_row, n_col, sq_colour, back_colour):
    exp = expyriment.design.Experiment(background_colour = back_colour) 
    control.initialize(exp)
    expyriment.control.start(exp)
    
    exp.screen.background_colour = back_colour
    exp.screen.clear()

    width, height = exp.screen.size
    figure_width = int(sq_size * n_col + (n_col -1) * sp_bt_sq)
    figure_height = int(sq_size * n_row + (n_row -1) * sp_bt_sq)
    square_size = (sq_size, sq_size)

    start_x = -figure_width // 2 + sq_size // 2
    start_y = -figure_height //2 + sq_size // 2

    for i in range(n_col):
        for j in range(n_row):
            x = start_x + i* (sq_size + sp_bt_sq)
            y = start_y + j* (sq_size + sp_bt_sq)
            square = stimuli.Rectangle(size = square_size, colour = sq_colour, position = (x,y))
            square.present(clear = False, update = False)
    exp.screen.update()
    exp.clock.wait(5000)
    control.end()

control.set_develop_mode()
hermann(sq_size=50, sp_bt_sq=30, n_row=10,n_col= 10, sq_colour=(0,0,0), back_colour=(225,225,225))
