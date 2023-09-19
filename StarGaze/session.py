from exptools2.core import Session
import numpy as np
import pandas as pd
from psychopy import tools, logging
import scipy.stats as ss
from stimuli import StarStim
from trial import StarTrial, DummyWaiterTrial, OutroTrial
import os
opj = os.path.join
opd = os.path.dirname

class StarSession(Session):
    def __init__(
        self, 
        output_str, 
        output_dir, 
        settings_file, 
        condition=None
        ):
        """ Initializes StroopSession object.

        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs), e.g., "sub-01_task-stroop_run-1"
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        eyetracker_on: bool, optional
            Make link with eyetracker during experiment, default is True
        condition: str, optional
            Which conditions to include in the experiment; options are 'LR' (for left & right hand movement), "LB" (left hand & both hands), and "RB" (right hand & both hands)
        """
        super().__init__(
            output_str, 
            output_dir=output_dir, 
            settings_file=settings_file
        )  # initialize parent class!

        self.duration           = self.settings['design'].get('stim_duration')
        self.outro_trial_time   = self.settings['design'].get('end_duration')
        self.start_duration     = self.settings['design'].get('start_duration')
        self.stim_duration      = self.settings['design'].get('stim_duration')
        self.static_isi         = self.settings['design'].get('static_isi')
        self.intended_duration  = self.settings['design'].get('intended_duration')
        self.star_points        = self.settings['design'].get('star_points')
        self.n_repeats          = self.settings['design'].get('n_repeats')
        self.condition          = condition
        self.size_cue           = self.settings['stimuli'].get('cue_size')
        self.color_cue          = self.settings['stimuli'].get('cue_color')

        # define dot as fixation
        self.StarStim = StarStim(
            self,
            units="deg",
            size=self.size_cue,
            fillColor=self.color_cue
        )
        
        # draw into memory
        self.StarStim.draw()


        # check demo mode
        if self.condition == "demo":
            self.n_repeats = 2
            self.start_duration = 2
            self.outro_trial_time = 2
        
        # traverse spokes of star with saccades and smooth pursuit
        self.n_trials = self.star_points*self.n_repeats

    def create_trials(self):
        """ Creates trials (ideally before running your session!) """

        # calculate full time of experiment
        self.total_experiment_time = self.start_duration + (self.n_trials * self.stim_duration) + self.outro_trial_time

        # check if we should add time to meet intended_duration
        self.add_to_total = 0
        if self.condition != "demo":
            if isinstance(self.intended_duration, (int,float)):
                if self.total_experiment_time < self.intended_duration:
                    self.add_to_total = self.intended_duration-self.total_experiment_time
                elif self.intended_duration<self.total_experiment_time:
                    raise ValueError(f"WARNING: intended duration ({self.intended_duration}) is smaller than total experiment time ({self.total_experiment_time})")
            
        self.total_experiment_time += self.add_to_total
        self.outro_trial_time += self.add_to_total
        print(f"Total experiment time = {round(self.total_experiment_time,2)}s (added {round(self.add_to_total,2)}s), with {self.n_repeats}x {self.star_points} spokes")
        
        # baseline trial beginning exp
        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=0,
            phase_durations=[np.inf, self.start_duration],
            phase_names=["dummy","intro"]
        )

        # baseline trial end of exp
        outro_trial = OutroTrial(
            session=self,
            trial_nr=self.n_trials+1,
            phase_durations=[self.outro_trial_time],
            phase_names=["outro"],
            txt='')
        
        # parameters
        self.events = ["saccade","pursuit"] 
        self.n_events = len(self.events)
        self.eye_movements = np.tile(np.arange(0,self.n_events), self.star_points)

        # shuffle blocks if you want
        if self.settings['design'].get('randomize'):
            np.random.shuffle(self.movement)

        # get positions
        self.star_anchors = self.settings["stimuli"].get("star_anchors")
        self.positions = get_positions(self.star_anchors, self.n_repeats)

        self.trials = [dummy_trial]
        for i in range(self.n_trials):
            
            # get number of steps for each event
            event_type = self.events[self.eye_movements[i]]
            if event_type == "saccade":
                steps = self.settings["design"].get("steps_saccade")
            else:
                steps = self.settings["design"].get("steps_pursuit")

            # get the end point per trial
            start_pos = self.positions[i]
            if i<(self.n_trials-1):
                end_pos = self.positions[i+1]
            else:
                end_pos = self.positions[0]

            print(f"trial #{i}\t| start = {start_pos}\t| end = {end_pos}")

            # calculate positions along line between points
            a = Point(*start_pos)
            b = Point(*end_pos)

            line = a.line_function(b)
            x_vals = np.linspace(start_pos[0],end_pos[0],steps)

            # fill in x in line function
            moving_coordinates = []
            for x in x_vals:
                y = line(x=x)
                moving_coordinates.append((x,y))
            
            # append trial
            self.trials.append(
                StarTrial(
                    session=self,
                    trial_nr=1+i,
                    phase_durations=[self.stim_duration],
                    phase_names=['stim'],
                    parameters={
                        'condition': event_type,
                        'n_steps': steps
                    },
                    coords=moving_coordinates,
                    timing='seconds',
                    verbose=True))
            
        self.trials.append(outro_trial)
                    
    def run(self):
        """ Runs experiment. """
        self.create_trials()  # create them *before* running!
        self.start_experiment()
        for trial in self.trials:
            trial.run()

        self.close()

def slope(dx, dy):
    return (dy / dx) if dx else None

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def halfway(self, target):
        midx = (self.x + target.x) / 2
        midy = (self.y + target.y) / 2
        return Point(midx, midy)

    def distance(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        return (dx*dx + dy*dy) ** 0.5

    def reflect_x(self):
        return Point(-self.x,self.y)

    def reflect_y(self):
        return Point(self.x,-self.y)

    def reflect_x_y(self):
        return Point(-self.x, -self.y)

    def slope_from_origin(self):
        return slope(self.x, self.y)

    def slope(self, target):
        return slope(target.x - self.x, target.y - self.y)

    def y_int(self, target):       # <= here's the magic
        return self.y - self.slope(target)*self.x

    def line_equation(self, target):
        slope = self.slope(target)

        y_int = self.y_int(target)
        if y_int < 0:
            y_int = -y_int
            sign = '-'
        else:
            sign = '+'

        return 'y = {}x {} {}'.format(slope, sign, y_int)

    def line_function(self, target):
        slope = self.slope(target)
        y_int = self.y_int(target)
        def fn(x):
            return slope*x + y_int
        return fn

def get_positions(pos, n_repeats):

    all_pos = pos
    for _ in range(n_repeats-1):
        all_pos += pos

    return all_pos


# iti function based on negative exponential
def _return_itis(mean_duration, minimal_duration, maximal_duration, n_trials):
    itis = np.random.exponential(scale=mean_duration-minimal_duration, size=n_trials)
    itis += minimal_duration
    itis[itis>maximal_duration] = maximal_duration
    return itis

def iterative_itis(mean_duration=6, minimal_duration=3, maximal_duration=18, n_trials=None, leeway=0, verbose=False):
    
    nits = 0
    itis = _return_itis(
        mean_duration=mean_duration,
        minimal_duration=minimal_duration,
        maximal_duration=maximal_duration,
        n_trials=n_trials)

    total_iti_duration = n_trials * mean_duration
    min_iti_duration = total_iti_duration - leeway
    max_iti_duration = total_iti_duration + leeway
    while (itis.sum() < min_iti_duration) | (itis.sum() > max_iti_duration):
        itis = _return_itis(
            mean_duration=mean_duration,
            minimal_duration=minimal_duration,
            maximal_duration=maximal_duration,
            n_trials=n_trials)
        nits += 1

    if verbose:
        print(f'ITIs created with total ITI duration of {round(itis.sum(),2)}s after {nits} iterations')    

    return itis
