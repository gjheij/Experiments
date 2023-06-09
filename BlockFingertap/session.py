from exptools2.core import Session
import numpy as np
import pandas as pd
from psychopy import tools, logging
import scipy.stats as ss
from stimuli import FixationCross, MotorStim, MotorMovie
from trial import MotorTrial, DummyWaiterTrial, OutroTrial
import os
opj = os.path.join
opd = os.path.dirname

class MotorSession(Session):
    def __init__(self, output_str, output_dir, settings_file, condition=None):
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
        super().__init__(output_str, output_dir=output_dir, settings_file=settings_file)  # initialize parent class!

        self.duration           = self.settings['design'].get('stim_duration')
        self.n_repeats          = self.settings['design'].get('n_repeats')
        self.outro_trial_time   = self.settings['design'].get('end_duration')
        self.unilateral_hand    = self.settings['design'].get('unilateral_hand')
        self.stim_height        = self.settings['various'].get('text_height')
        self.stim_width         = self.settings['various'].get('text_width')
        self.fixation_width     = self.settings['stimuli'].get('fixation_width')
        self.fixation_color     = self.settings['stimuli'].get('fixation_color')
        self.text_color         = self.settings['stimuli'].get('text_color')
        self.start_duration     = self.settings['design'].get('start_duration')
        self.stim_duration      = self.settings['design'].get('stim_duration')
        self.static_isi         = self.settings['design'].get('static_isi')

        # add demo mode with 1 iteration of right/left stim
        if condition == "demo":
            self.events = ["right","left"]
            self.outro_trial_time = 2
            self.stim_duration = 2
            self.static_isi = 2
            self.n_repeats = 1
            self.start_duration = 0
        elif condition == "RL":
            self.events = ["right","left"]
        elif condition == "LB":
            self.events = ["left","both"]
        elif condition == "RB":
            self.events = ["right","both"]
        elif condition == "RBL":
            self.events = ["right","left","both"]
        else:
            raise ValueError(f"Condition must be one of 'RL/LR', 'LB/BL', or 'RB/BR', or 'all [R/L/both]' not '{condition}'")

        self.n_events = len(self.events)
        self.n_trials = self.n_repeats*self.n_events

        # self.unilateral_movie   = "1hand.mp4"
        self.movie_both = "2hands.mp4"
        self.movie_left = "lhand.mp4"
        self.movie_right = "rhand.mp4"

        # define crossing fixation lines
        self.fixation = FixationCross(
            win=self.win, 
            lineWidth=self.fixation_width, 
            color=self.fixation_color)

        for stim in self.events:
            # define stim:
            if stim == "both":
                self.display_instructions = f"MOVE BOTH HANDS"
            else:
                self.display_instructions = f"MOVE {stim.upper()} HAND"

            # use movies or text..
            if self.settings["stimuli"].get("use_movies"):
                stim_obj = MotorMovie(
                    self,
                    movie_file=getattr(self, f"movie_{stim}"),
                    size_factor=self.settings["stimuli"].get("movie_window_scale_factor"))
            else:
                stim_obj  = MotorStim(
                    session=self,
                    color=self.text_color,
                    text=self.display_instructions)
            
            setattr(self, f"stim_{stim}", stim_obj)
            stim_obj.draw()
            
        # check if we want a cue before stim onset
        self.cue_time = self.settings["design"].get("cue_time")
        if isinstance(self.cue_time, (int,float)):
            self.cue = True
            self.cue_color = self.settings["stimuli"].get("cue_color")
        else:
            self.cue = False

    def create_trials(self):
        """ Creates trials (ideally before running your session!) """

        if not isinstance(self.static_isi, (int,float)):
            itis = iterative_itis(
                mean_duration=self.settings['design'].get('mean_iti_duration'),
                minimal_duration=self.settings['design'].get('minimal_iti_duration'),
                maximal_duration=self.settings['design'].get('maximal_iti_duration'),
                n_trials=self.n_trials,
                leeway=self.settings['design'].get('total_iti_duration_leeway'),
                verbose=True)
        else:
            itis = np.full(self.n_trials, self.static_isi)

        # calculate full time of experiment
        self.total_experiment_time = self.start_duration + (self.n_trials * self.stim_duration) + itis.sum() + self.outro_trial_time
        print(f"Total experiment time = {self.total_experiment_time}s, with {self.n_repeats}x {self.events} each")

        dummy_trial = DummyWaiterTrial(
            session=self,
            trial_nr=0,
            phase_durations=[np.inf, self.start_duration])

        outro_trial = OutroTrial(
            session=self,
            trial_nr=self.n_trials+2,
            phase_durations=[self.outro_trial_time],
            txt='')
        
        # parameters
        self.movement = np.tile(np.arange(0,self.n_events), self.n_repeats)
        
        # shuffle blocks if you want
        if self.settings['design'].get('randomize'):
            np.random.shuffle(self.movement)

        self.trials = [dummy_trial]
        for i in range(self.n_trials):
            
            # append trial
            self.trials.append(
                MotorTrial(
                    session=self,
                    trial_nr=1+i,
                    phase_durations=[itis[i], self.stim_duration],
                    phase_names=['iti','stim'],
                    parameters={'condition': self.events[self.movement[i]]},
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
