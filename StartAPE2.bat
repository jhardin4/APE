CALL activate.bat
SET batPath=%~dp0
ECHO Running %batPath%startup.py...

python %batPath%startup.py
pause
