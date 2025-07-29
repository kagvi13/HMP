@echo off
REM === CONFIGURATION ===
set ENABLE_NOTEBOOK=true
set ENABLE_MESH=true
set NOTEBOOK_PATH=user_notebook.txt
set MESH_PORT=8080

echo --------------------------
echo Installing requirements...
echo --------------------------
pip install -r requirements.txt

echo --------------------------
echo Running HMP REPL-agent...
echo --------------------------

set ARGS=

if "%ENABLE_NOTEBOOK%"=="true" (
    set ARGS=%ARGS% --enable-user-notebook --notebook-path %NOTEBOOK_PATH%
)

if "%ENABLE_MESH%"=="true" (
    set ARGS=%ARGS% --enable-mesh --mesh-port %MESH_PORT%
)

python repl.py %ARGS%

pause
