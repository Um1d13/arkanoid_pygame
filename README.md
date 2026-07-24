# PyGame Arkanoid

## Requirements

You'll need

1. Git
1. Python3 for your system
1. Python VENV (installs with Python)

To check, you can use commands listed below. If you'll get a "Command not found" error instead of the version, that means you don't have a certain tool installed correctly, so you'll need to reinstall it.

1. `git -v` - to check your git.
1. `python3 --version` - to check your Python. Version 3.11+ is recommended. Older versions are ok, but it's not guaranteed that the game will run on older versions.

## Installation and local run

1. Clone this repo: `git clone https://github.com/uptothetop/arkanoid_pygame.git`
1. Go to the app's folder: `cd arkanoid_pygame`
1. Set up your virtual env (venv): `python3 -m venv env`
1. АActivate your venv: 
    1. OSX, Linux, Unix systems: `source env/bin/activate`
    1. For Windows use Powershell: `.\venv\bin\Activate.ps1`
1. After activation there will be venv name in brackets in your terminal, for example `(env)`
1. Install dependencies: `pip install -r requirements.txt`
1. Run the app: `python3 main.py`

After that you should see an empty window titled as "Arkanoid" - that means that you've installed everything correctly
