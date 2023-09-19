from psychopy.visual import Circle

class StarStim(object):   

    def __init__(self, session, *args, **kwargs):

        self.session = session
        self.star_point = Circle(
            win=self.session.win,
            # opacity=0.1,
            edges=128,
            *args,
            **kwargs)

    def draw(self):
        self.star_point.draw()      