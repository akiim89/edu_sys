#!/usr/bin/env python
import os, subprocess, filecmp

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VENV_DIR=os.path.join(BASE_DIR, 'env')

def new_venv(msg):
    print('Rebuilding venv: %s' % msg)
    subprocess.check_call([os.path.join(BASE_DIR, 'scripts/buildenv')], shell=True)

venv_requirements_file = os.path.join(VENV_DIR, 'requirements.txt')
requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
if not os.path.exists(venv_requirements_file):
    new_venv('File does not exist: %s' % venv_requirements_file)
if not filecmp.cmp(requirements_file, venv_requirements_file):
    new_venv('File %s differs from %s' % (venv_requirements_file, requirements_file))
    
# Verify we can activate the virtualenv
activate_this = os.path.join(VENV_DIR, 'bin/activate_this.py')
try:
    # Code from http://stackoverflow.com/a/33637378/109044
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})
except:
    new_venv('Could not activate venv')
