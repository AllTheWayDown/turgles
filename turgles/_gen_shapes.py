import turtle

screen = turtle.Screen()


for name, shape in screen._shapes.items():
    if name == 'blank':
        continue
    maxima = 0
    print("'%s': {" % name)
    print("    'vertex': (")
    output = []
    #import pdb; pdb.set_trace()
    for x, y in shape._data:
        maxima = max(maxima, abs(x), abs(y))
        output.append((y, -x))
    for x, y in output:
        print("        %f, %f," % (x/maxima, y/maxima))
    print("    ),")
    print("    'index': (,")
    print("    ),")
    print("},")




