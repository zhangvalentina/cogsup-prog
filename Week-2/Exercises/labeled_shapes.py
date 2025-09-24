<<<<<<< HEAD
from expyriment import design, control, stimuli
from expyriment.misc import geometry

control.set_develop_mode()

exp = design.Experiment(name='Labeled Shapes')
control.initialize(exp)

# Shapes
triangle = stimuli.Shape(vertex_list=geometry.vertices_regular_polygon(3, 25))
triangle.colour = (128,0,128)
triangle.position = (-150, 0)

hexagon = stimuli.Shape(vertex_list=geometry.vertices_regular_polygon(6, 25))
hexagon.colour = (255,255,0)
hexagon.position = (150, 0)

# Lines (as shapes)
line_length = 50
line_triangle = stimuli.Shape(vertex_list=[(0,0),(0,-line_length)])
line_triangle.colour = (255,255,255)
line_triangle.position = (triangle.position[0], triangle.position[1] + 25)

line_hexagon = stimuli.Shape(vertex_list=[(0,0),(0,-line_length)])
line_hexagon.colour = (255,255,255)
line_hexagon.position = (hexagon.position[0], hexagon.position[1] + 25)

# Labels
label_triangle = stimuli.TextLine("triangle")
label_triangle.colour = (255,255,255)
label_triangle.text_size = 20
label_triangle.position = (triangle.position[0], triangle.position[1] + 25 + line_length + 20)

label_hexagon = stimuli.TextLine("hexagon")
label_hexagon.colour = (255,255,255)
label_hexagon.text_size = 20
label_hexagon.position = (hexagon.position[0], hexagon.position[1] + 25 + line_length + 20)

control.start(subject_id=1)

triangle.present(clear=True, update=False)
hexagon.present(clear=False, update=False)
line_triangle.present(clear=False, update=False)
line_hexagon.present(clear=False, update=False)
label_triangle.present(clear=False, update=False)
label_hexagon.present(clear=False, update=True)  # draw everything at once

exp.keyboard.wait()
control.end()

=======
from expyriment import design, control, stimuli
from expyriment.misc import geometry

control.set_develop_mode()

exp = design.Experiment(name='Labeled Shapes')
control.initialize(exp)

# Shapes
triangle = stimuli.Shape(vertex_list=geometry.vertices_regular_polygon(3, 25))
triangle.colour = (128,0,128)
triangle.position = (-150, 0)

hexagon = stimuli.Shape(vertex_list=geometry.vertices_regular_polygon(6, 25))
hexagon.colour = (255,255,0)
hexagon.position = (150, 0)

# Lines (as shapes)
line_length = 50
line_triangle = stimuli.Shape(vertex_list=[(0,0),(0,-line_length)])
line_triangle.colour = (255,255,255)
line_triangle.position = (triangle.position[0], triangle.position[1] + 25)

line_hexagon = stimuli.Shape(vertex_list=[(0,0),(0,-line_length)])
line_hexagon.colour = (255,255,255)
line_hexagon.position = (hexagon.position[0], hexagon.position[1] + 25)

# Labels
label_triangle = stimuli.TextLine("triangle")
label_triangle.colour = (255,255,255)
label_triangle.text_size = 20
label_triangle.position = (triangle.position[0], triangle.position[1] + 25 + line_length + 20)

label_hexagon = stimuli.TextLine("hexagon")
label_hexagon.colour = (255,255,255)
label_hexagon.text_size = 20
label_hexagon.position = (hexagon.position[0], hexagon.position[1] + 25 + line_length + 20)

control.start(subject_id=1)

triangle.present(clear=True, update=False)
hexagon.present(clear=False, update=False)
line_triangle.present(clear=False, update=False)
line_hexagon.present(clear=False, update=False)
label_triangle.present(clear=False, update=False)
label_hexagon.present(clear=False, update=True)  # draw everything at once

exp.keyboard.wait()
control.end()

>>>>>>> 02a71c0a65edeed1351f93ad4feb5ff09fa0dccd
