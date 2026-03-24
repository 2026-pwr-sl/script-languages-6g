
# Project Documentation

## 1. Project structure

The repository is organized into the following main directories and files:

- src/ - application source code
- tests/ - tests for project logic
- docs/ - project documentation
- data/ - data files such as exported JSON
- README.md - general repository overview and quick start
- requirements.txt - Python dependencies

## 2. Modules

### src/main.py
This is the entry point of the program.
It uses argparse to provide a simple command-line interface.

Supported options:
- --show-team - display all team members
- --count - display the number of team members
- --greet NAME - print a greeting for the provided name

### src/team.py
This module stores team data and provides operations on that data.

Example functions:
- count_team_members(...) - returns the number of team members
- display_team_members(...) - displays the team members
- team_members - stores the team data

### src/utils.py
This module contains helper functions related to formatting output.

Example function:
- format_greeting(name) - returns a greeting message for the given name

## 3. How to run the program

From the root of the repository, run the program with:

python3 src/main.py [option]

Available options:

python3 src/main.py --show-team
Displays all team members.

python3 src/main.py --count
Displays the number of team members.

python3 src/main.py --greet Lucjan
Prints a greeting for the provided name.

You can also combine options:

python3 src/main.py --show-team --count

Example:

python3 src/main.py --show-team --count --greet Lucjan

If you run the program without any options:

python3 src/main.py

the help message will be displayed.

## 4. CLI usage summary

- --show-team - display all team members
- --count - display the number of team members
- --greet NAME - print a greeting for the provided name

## 5. Summary

This project is divided into small modules to improve readability and teamwork:
- main.py handles the command-line interface and program flow
- team.py handles team-related data and operations
- utils.py handles formatting and helper functions
