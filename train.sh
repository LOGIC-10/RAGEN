#!/bin/bash

# Default environment
ENV_NAME=${1:-"sokoban"}

export PYTHONHASHSEED=10000

# Get and execute the training command
if [ "$1" = "deepreport" ]; then
    CONFIG_PATH="ragen/env/deepreport/config.yaml"
else
    python ragen/train.py "$ENV_NAME" "$@" | bash
fi