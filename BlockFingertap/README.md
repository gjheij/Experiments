# Motor experiment

Simple finger-tapping/clenching/moving experiment. To be run as:

```python main.py <sub ID> <ses ID> <run ID> <condition>```

e.g.,:

```python main.py 01 1 1 RL```

Use numbers only for `sub ID`, `ses ID`, and `run ID`; we'll make the folder `sub-<sub_ID>_ses-<ses-ID>_run-<run_ID>_task-<condition>`

We can deal with the following conditions:

- Left vs right         (condition = `RL`)
- Left vs both          (condition = `BL`)
- Right vs both         (condition = `BR`)
- Right vs left vs both (condition = `RBL`)
- demo                  (condition = `demo`) > show brief version of experiment to show your subject what it looks like

The experiment can be run as a block paradigm or event-related paradigm. By default, it's set to do 7 blocks of each event specified (e.g., `left-right`) of 30 seconds, with 30 seconds rest in between, and 30 at the end of the experiment (=870s). The following parameters in the [settings-file](settings.yml) can be used to tailor your block experiment:

- `start_duration`      (baseline at the end of the beginning. By default 0 as the block-design starts with baseline)
- `end_duration`        (baseline at the end of the experiment, as it ends with a stimulus-block)
- `static_isi`          (length of rest periods in between activation blocks)
- `stim_duration`       (length of activation period)

If you keep these parameters the same, you have a block design. Change the following items to make it event-related:

- `static_isi` must be set to `"None"` > this will use the `iti` variables to be used to create a set of inter-stimulus intervals based on a negative exponential
- `stim_duration`: can be max 3 seconds to be effective
- `randomize`: advised to be set to `True` so that the events are randomized

Other parameters than can be set:

- `use_movies`: by default, the stimulus entails displaying text like `MOVE RIGHT HAND`. Alternatively, you can use animations of the movement that needs to be made. To do this, set `use_movies` to `True`
- `randomize`: randomize the blocks/events, rather than sticking to a fixed order (advised for event-related design)
- `cue_time`: we can present a cue by changing the color of the fixation cross shortly before the onset of an event to let the participant know a stimulus is coming. This can reduce the element of surprise and improve reaction times. To turn off this cue, set `cue_time` to `"None"`
