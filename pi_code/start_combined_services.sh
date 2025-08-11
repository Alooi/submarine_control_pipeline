#!/bin/bash

# Start the combined server using the virtual environment's python
# Do NOT set PYTHONHOME, as this breaks venvs. Only set PATH and VIRTUAL_ENV.

ENV_PATH="/home/dwe/myenv"
PYTHON="$ENV_PATH/bin/python"

env -i PATH="$ENV_PATH/bin:/usr/bin:/bin" VIRTUAL_ENV="$ENV_PATH" "$PYTHON" /home/dwe/pi_code/combined_server.py