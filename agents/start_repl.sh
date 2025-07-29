#!/bin/bash

# === CONFIG ===
ENABLE_NOTEBOOK=true
ENABLE_MESH=true
MESH_PORT=8080
NOTEBOOK_PATH="user_notebook.txt"

# === INSTALL DEPENDENCIES ===
echo "--------------------------"
echo "Installing requirements..."
echo "--------------------------"
pip install -r requirements.txt

# === BUILD ARGUMENTS ===
ARGS=""

if [ "$ENABLE_NOTEBOOK" = true ]; then
  ARGS="$ARGS --enable-user-notebook --notebook-path $NOTEBOOK_PATH"
fi

if [ "$ENABLE_MESH" = true ]; then
  ARGS="$ARGS --enable-mesh --mesh-port $MESH_PORT"
fi

# === RUN AGENT ===
echo "--------------------------"
echo "Running HMP REPL-agent..."
echo "--------------------------"
python repl.py $ARGS
