#!/bin/bash

VENV_DIR="/home/dwe/pi_code/myenv"
SCRIPT_DIR="/home/dwe/pi_code"

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

echo "Using Python: $(which python3)"
echo "Python version: $(python3 --version)"
echo "Installed packages:"
pip list

echo "Running video_feeder.py with sys.path:"
python3 -c "import sys; print('\n'.join(sys.path))"

python3 "$SCRIPT_DIR/video_feeder.py"
