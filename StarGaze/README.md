# Motor experiment

Simple finger-tapping/clenching/moving experiment. To be run as:

```python main.py <sub ID> <ses ID> <run ID> <condition>```

e.g.,:

```python main.py 01 1 1 RL```

Use numbers only for `sub ID`, `ses ID`, and `run ID`; we'll make the folder `sub-<sub_ID>_ses-<ses-ID>_run-<run_ID>_task-<condition>`

If you run `python main.py` by itself, you'll be able to fill in information by hand.

We can deal with the following conditions:
- Left or right or both  (condition = `R`/`L`/`both`)
- Left vs right         (condition = `RL`)
- Left vs both          (condition = `BL`)
- Right vs both         (condition = `BR`)
- Right vs left vs both (condition = `RBL`/`all`)
- demo                  (condition = `demo`) > show brief version of experiment to show your subject what it looks like

The experiment can be run as a block paradigm or event-related paradigm. The following parameters in the [settings-file](settings.yml) can be used to tailor your block experiment:

- `start_duration`      (baseline at the end of the beginning. By default 0 as the block-design starts with baseline)
- `end_duration`        (baseline at the end of the experiment, as it ends with a stimulus-block)
- `static_isi`          (length of rest periods in between activation blocks)
- `stim_duration`       (length of activation period)

If you keep these parameters the same, you have a block design. Change the following items to make it event-related:

- `static_isi` must be set to `"None"` > this will use the `iti` variables to be used to create a set of inter-stimulus intervals based on a negative exponential
- `stim_duration`: can be max 3 seconds to be effective
- `randomize`: advised to be set to `True` so that the events are randomized

Other parameters than can be set:

- `n_repeats`: number of times to repeat the set of selected stimuli. E.g., if condition == `RL` we'll use 2 stimuli (`left` and `right`). The total number of trials is then 2*`n_repeats`. Similarly, if condition == `RBL`, we'll use 3 stimuli. The total number of trials is then 3*`n_repeats`.
- `use_movies`: by default, the stimulus entails displaying text like `MOVE RIGHT HAND`. Alternatively, you can use animations of the movement that needs to be made. To do this, set `use_movies` to `True`
- `randomize`: randomize the blocks/events, rather than sticking to a fixed order (advised for event-related design)
- `intended_duration`: this can be the full duration (in seconds) of your acquisition. Settings this value will ensure the experiment runs until the end of the sequence. This is mainly important for visual experiments, but it also enhances subject experience (bit sloppy if the experiment is done while you're still scanning..)
