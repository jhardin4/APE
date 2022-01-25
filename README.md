# Apparatus Procedure Executor (APE)

Automation middleware for accelerating integration and autonomy

APE is a Python middleware for corrdinating multiple machines (automation) and
maintaining the providence of the information used to run these machines.

## Getting started

Although it is not essential, it assumed that Anaconda has been installed as a
way to quickly get most of the necessary packages and IDE (Spyder).

Several example files of how APE can be used are in the Examples folders.

### First simulation run

Look in Examples/FlexPrinterMonolith folder and copy Example_Monolith.py and
TemplateTPGen.py into the root folder of APE (the same folder as this file).

Open Example_Monolith.py in an IDE of your choice.

### Setting up on a new physical system

In practical use, wrapping intended function in Python is a good first step.

Once that is done, the Python wrapper can be reformated into a Device by
adding simulation and and logging functionality.  This process will also
define the elemental procedures that will be used by the larger APE 
architecture.


### Revision control

It is reccommended that APE version specific to a project be stored in a
online git repository.  This ensures that remote work is on the automation
is on the latest version and enable quick tracking of new errors at the 
machine.  To facilitate this on windows computers, an example git batch file
(Win_git_push.bat) has been included. It is currently set up for our GCP
repositories but can be modified for others.




