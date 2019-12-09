::
::Find the Python Version Pathway
::
@echo off
for /f %%a in ('REG QUERY "HKLM\SOFTWARE\Python\PythonCore"') do (set pyVersionKeyPath=%%a)
echo %pyVersionKeyPath%
::
::Find the Anaconda Pathway
::
for /f "tokens=3*" %%a in ('REG QUERY "%pyVersionKeyPath%\InstallPath"') do (set anacondaKeyPath=%%a)
echo %anacondaKeyPath%
::
::Activate activate.bat in Anaconda
CALL %anacondaKeyPath%\Scripts\activate.bat
ECHO Running %anacondaKeyPath%\Scripts\activate.bat
::
:: Finds path of .bat and runs startup.py in Python.
::   (.bat file needs to be in the same file as startup.py)
:: 
SET batPath=%~dp0
ECHO Running %batPath%startup.py
python %batPath%startup.py
::
::Exits cmd window when startup.py is closed
::
exit