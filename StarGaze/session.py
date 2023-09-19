from exptools2.core import Session
import numpy as np
from stimuli import StarStim
from trial import StarTrial, DummyWaiterTrial, OutroTrial
import os
from utils import *
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