from __future__ import division, print_function, absolute_import

from turgles.tk_colors import COLORS


class Turgle(object):
    """Implementation of NinjaTurtle's backend api.

    Mainly contains methods for maniuplating the render data.
    """

    def __init__(self, renderer, model):
        self.renderer = renderer
        self.model = model
        self._shape = 'classic'

    def shape(self, shape=None):
        """We need to shift buffers in order to change shape"""
        if shape is None:
            return self._shape
        self.model.data = self.renderer.manager.set_shape(self.model.id, shape)
        self._shape = shape

    def shapesize(self, stretch_wid=None, stretch_len=None, outline=None):
        #TODO: outline
        if stretch_wid is stretch_len is outline is None:
            stretch_wid = self.model.data[2]
            stretch_len = self.model.data[3]
            return stretch_wid, stretch_len, None
        if stretch_wid == 0 or stretch_len == 0:
            raise Exception("stretch_wid/stretch_len must not be zero")
        if stretch_wid is not None:
            if stretch_len is None:
                self.model.data[2] = self.model.data[3] = stretch_wid
            else:
                self.model.data[2] = stretch_wid
                self.model.data[3] = stretch_len

    turtlesize = shapesize

    def _get_color_values(self, color):
        if color in COLORS:
            color = COLORS[color]
        elif color[0] == '#':
            color = (
                int(color[1:3], 16),
                int(color[3:5], 16),
                int(color[5:7], 16)
            )
        else:
            assert len(color) == 3

        #TODO 0-255 color range
        return color

    def color(self, *args):
        n = len(args)
        if n == 0:
            return tuple(self.model.data[8:10]), (0, 0, 0)
        if n == 1:
            # either a colorstr or tuple
            values = self._get_color_values(args[0])
            self.model.data[8:10] = values
            # TODO: set pencolor
        elif n == 3:
            # single color, rgb
            values = self._get_color_values(args)
            self.model.data[8:10] = values
            # TODO: set pencolor
        elif n == 2:
            # two separate colors
            self.pencolor(args[0])
            self.fillcolor(args[1])
        else:
            raise Exception("Invalid color arguments")

    def pencolor(self, *args):
        if len(args) == 0:
            #TODO: change to pencolor
            return tuple(self.model.data[8:11])
        elif len(args) == 1:
            color_vals = self._get_color_values(args[0])
        else:
            # rgb params
            color_vals = self._get_color_values(args)
        #TODO change to pencolor
        self.model.data[8:11] = color_vals

    def fillcolor(self, *args):
        if len(args) == 0:
            return tuple(self.model.data[8:11])
        elif len(args) == 1:
            color_vals = self._get_color_values(args[0])
        else:
            # rgb params
            color_vals = self._get_color_values(args)
        self.model.data[8:11] = color_vals

    def hideturtle(self):
        # HAAAAAACCKK
        self._set_color = self.model.data[8:10]
        self.pencolor('#ffffff')

    ht = hideturtle

    def showturtle(self):
        # HAAAAAACCKK
        if self._set_color:
            self.model.data[8:10] = self._set_color
        self._set_color = None

    st = showturtle

    def isvisible(self):
        # TODO
        return True

    def pendown(self):
        pass

    pd = down = pendown

    def penup(self):
        pass

    pu = up = penup

    def pensize(self, size):
        pass

    width = pensize

    def pen(self, **kwargs):
        pass

    def isdown(self):
        return False

    def begin_fill():
        pass

    def end_fill():
        pass

    def dot(self):
        pass

    def stamp(self):
        pass

    def clear():
        pass

    def clearstamp(self, id):
        pass

    def clearstamps(self):
        pass

    def write(self):
        pass
