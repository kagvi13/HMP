#!/bin/bash

# === INSTALL DEPENDENCIES ===
echo "--------------------------"
echo "Installing requirements..."
echo "--------------------------"
pip install -r requirements.txt

# === RUN AGENT ===
echo --------------------------
echo Running initialization...
echo --------------------------
python repl.py
