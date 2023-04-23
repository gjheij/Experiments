import numpy as np
from psychopy.visual import TextStim, ShapeStim, RadialStim, MovieStim3


class FixationCross(object):

    def __init__(self, win, lineWidth, color, *args, **kwargs):
        self.color      = color
        self.linewidth  = lineWidth
        self.fixation   = ShapeStim(
            win, 
            vertices=((0, -0.1), (0, 0.1), (0,0), (-0.1,0), (0.1, 0)),
            lineWidth=self.linewidth,
            closeShape=False,
            lineColor=self.color)

    def draw(self):
        self.fixation.draw()

    def setColor(self, color):
        self.fixation.color = color
        self.color = color
        
class MotorStim(object):

    def __init__(self, session, text, color="black", **kwargs):
        self.session = session
        self.color = color
        self.text = TextStim(
            self.session.win, 
            text, 
            height=1, 
            pos=(0,0),
            wrapWidth=self.session.settings['various'].get('text_width'), 
            color=self.color,
            **kwargs)

    def draw(self):
        self.text.draw()

class MotorMovie():

    def __init__(
            self, 
        session, 
        movie_file=None, 
        size_factor=0.7, 
        *args, 
        **kwargs):

        self.session = session
        x,y = self.session.win.size
        new_size = [x*size_factor, y*size_factor]

        # initialize movies
        self.mov = MovieStim3(
            self.session.win, 
            filename=movie_file, 
            loop=True, 
            size=new_size,
            *args,
            **kwargs)
        
    def draw(self):
        self.mov.draw()
