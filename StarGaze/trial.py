import numpy as np
from exptools2.core import Trial
from psychopy.visual import TextStim

class StarTrial(Trial):

    def __init__(
        self, 
        session, 
        trial_nr, 
        phase_durations, 
        phase_names,
        parameters, 
        timing, 
        coords=None,
        verbose=True):

        """ Initializes a StroopTrial object.

        Parameters
        ----------
        session : exptools Session object
            A Session object (needed for metadata)
        trial_nr: int
            Trial nr of trial
        phase_durations : array-like
            List/tuple/array with phase durations
        phase_names : array-like
            List/tuple/array with names for phases (only for logging),
            optional (if None, all are named 'stim')
        parameters : dict
            Dict of parameters that needs to be added to the log of this trial
        timing : str
            The "units" of the phase durations. Default is 'seconds', where we
            assume the phase-durations are in seconds. The other option is
            'frames', where the phase-"duration" refers to the number of frames.
        verbose : bool
            Whether to print extra output (mostly timing info)
        """
        super().__init__(
            session, 
            trial_nr, 
            phase_durations, 
            phase_names,
            parameters, 
            timing, 
            load_next_during_phase=None, 
            verbose=verbose
        )

        self.condition = self.parameters['condition']
        self.session = session
        self.coordinates = coords
        self.time_per_coord = self.session.duration/len(self.coordinates)
        
        # get switch times
        self.switch_times = np.arange(self.time_per_coord,self.session.duration,self.time_per_coord)

        # correct for arrays where the last element is equal to the stimulus duration
        if np.isclose(self.switch_times[-1], self.session.duration):
            self.switch_times = np.arange(self.time_per_coord,(self.session.duration-self.time_per_coord),self.time_per_coord)

        # format the same way as presentation_time (flipped and negative)
        self.switch_times = -self.switch_times[::-1]
        self.coord_ix = 0
        self.pos = self.coordinates[0]
        
    def run(self):
        super().run()

    def draw(self):
        
        # loop through switch times based on active presentation time
        self.presentation_time = self.session.timer.getTime()
        if self.coord_ix < len(self.switch_times):
            if self.presentation_time < self.switch_times[self.coord_ix]:
                self.pos = self.coordinates[self.coord_ix]
            else:
                self.coord_ix += 1
        else:
            self.pos = self.coordinates[-1]
            
        # draw
        self.session.StarStim.star_point.setPos(self.pos)
        self.session.StarStim.draw()

    def get_events(self):
        events = super().get_events()

class InstructionTrial(Trial):
    """ Simple trial with instruction text. """

    def __init__(
        self, 
        session, 
        trial_nr, 
        phase_durations=[np.inf],
        txt=None, 
        keys=None, 
        *args,
        **kwargs):

        super().__init__(
            session, 
            trial_nr, 
            phase_durations, 
            *args,
            **kwargs)

        txt_height = self.session.settings['various'].get('text_height')
        txt_width = self.session.settings['various'].get('text_width')

        if txt is None:
            txt = '''Press any button to continue.'''

        self.text = TextStim(
            self.session.win, 
            txt, 
            height=txt_height, 
            wrapWidth=txt_width
        )
        self.keys = keys

    def draw(self):
        self.text.draw()

    def get_events(self):
        events = super().get_events()

        if self.keys is None:
            if events:
                self.stop_phase()
        else:
            for key, t in events:
                if key in self.keys:
                    self.stop_phase()


class DummyWaiterTrial(InstructionTrial):
    """ Simple trial with text (trial x) and fixation. """

    def __init__(
        self, 
        session, 
        trial_nr, 
        phase_durations=None,
        txt="Waiting for scanner triggers.", 
        *args,
        **kwargs):

        self.txt = txt
        super().__init__(
            session, 
            trial_nr, 
            phase_durations, 
            self.txt, 
            *args,
            **kwargs
        )

    def draw(self):
        if self.phase == 0:
            self.text.draw()

    def get_events(self):
        events = Trial.get_events(self)

        if events:
            for key, t in events:
                if key == self.session.mri_trigger:
                    if self.phase == 0:
                        self.stop_phase()

class OutroTrial(InstructionTrial):
    """ Simple trial with only fixation cross.  """

    def __init__(self, session, trial_nr, phase_durations, txt='', **kwargs):

        txt = ''''''
        super().__init__(session, trial_nr, phase_durations, txt=txt, **kwargs)

    def draw(self):
        pass
        # self.session.fixation.draw()
        
    def get_events(self):
        events = Trial.get_events(self)

        if events:
            for key, t in events:
                if key == 'space':
                    self.stop_phase()
