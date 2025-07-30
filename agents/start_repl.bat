@echo off
echo --------------------------
echo Installing requirements...
echo --------------------------
pip install -r requirements.txt

echo --------------------------
echo Running HMP REPL-agent...
echo --------------------------

python repl.py

pause
