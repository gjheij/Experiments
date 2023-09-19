import argparse
from datetime import datetime
import os
from psychopy import logging
from session import MotorSession
opj = os.path.join
opd = os.path.dirname

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('subject', default=None, nargs='?')
parser.add_argument('session', default=None, nargs='?')
parser.add_argument('run', default=None, nargs='?')
parser.add_argument('condition', default=None, nargs='?')

cmd_args = parser.parse_args()
subject, session, run, condition = cmd_args.subject, cmd_args.session, cmd_args.run, cmd_args.condition

if subject is None:
    subject = input('Subject? (999): ')
    subject = 999 if subject == '' else subject

if session is None:
    session = input('Session? (0): ')
    session = 0 if session == '' else session

if run is None:
    run = input('Run? (0): ')
    run = 0 if run == '' else run

if condition is None:
    condition = input('Condition? (RL): ')
    condition = "RL" if condition == '' else condition    

# conform to specific order
if condition == "LR":
    condition = "RL"
elif condition == "BR":
    condition = "RB"
elif condition == "BL":
    condition = "LB"
elif condition == "all":
    condition = "RBL"
elif condition == "demo":
    condition = "demo"    

output_str = f'sub-{subject}_ses-{session}_run-{run}_task-{condition}'
settings_fn = opj(opd(__file__), 'settings.yml')

output_dir = './logs/'+output_str

if os.path.exists(output_dir):
    logging.warn("Warning: output directory already exists. Renaming to avoid overwriting.")
    output_dir = output_dir + datetime.now().strftime('%Y%m%d%H%M%S')

# define session
session_object = MotorSession(
    output_str=output_str, 
    output_dir=output_dir, 
    settings_file=settings_fn,
    condition=condition)

logging.warn(f'Writing results to: {opj(session_object.output_dir, session_object.output_str)}')
session_object.run()
session_object.close()
