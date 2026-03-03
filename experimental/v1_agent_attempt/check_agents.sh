#!/bin/bash

echo "--------------------------"
echo "Installing requirements..."
echo "--------------------------"
pip install -r requirements.txt

echo --------------------------
echo Check agents...
echo --------------------------
python check_agents.py
