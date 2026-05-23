# Script Languages – Group 6g

## Group information
- **Group name:** 6g
- **Repository:** `script-languages-6g`

## Team members
- Efran Fernandez Fernandez
- Szymon Lisowski
- Oskar Nowakowski
- Lucjan Pucelak

## Project goal
The goal of this project is to learn the basics of teamwork with Python and GitHub.
The repository is used to practice collaboration, branches, commits, pull requests,
and the development of a simple Python program as a team.

## Project structure
- `src/` – source code
- `tests/` – tests
- `docs/` – documentation or notes
- `data/` – optional input data

## Instructions for running the program

1. Clone the repository:
   ```bash
   git clone https://github.com/2026-pwr-sl/script-languages-6g.git
   cd script-languages-6g
   ```

2. Check that Python 3 is installed:
   ```bash
   python3 --version
   ```

3. Run the main program:
   ```bash
   python3 src/main.py --show-team
   python3 src/main.py --count
   python3 src/main.py --greet Efran
   ```

4. Run the tests:
   ```bash
   python3 tests/test_main.py
   ```

## Team work summary

### Who was responsible for what
- Lucjan Pucelak – repository setup, responsibility dividing, documentation,  tests
- Efran Fernandez Fernandez – program development and functions
- Szymon Lisowski – repository managing, code review, maintenance, refactoring
- Oskar Nowakowski – project structure setup, code development support, tests

### Problems we encountered
- GitHub authentication and pushing changes from local branches
- working on separate branches and keeping them updated
- matching issue descriptions with the current function names in the code
- learning how to create pull requests and respond to review comments

### What we learned while working with Python and GitHub
- how to organize a simple Python project into folders such as `src`, `tests`, and `docs`
- how to run a Python program locally
- how to prepare simple tests for Python functions
- how to use GitHub Issues, branches, commits, and pull requests
- how code review works and why clear branch names and commit messages are important
- how to resolve merging conflicts
- how to collaborate and build a project together

## pycodestyle run 
```text
.\src\lab9\lab9.py:104:80: E501 line too long (86 > 79 characters)
.\src\lab9\lab9.py:550:80: E501 line too long (82 > 79 characters)
.\src\lab9\lab9.py:553:80: E501 line too long (82 > 79 characters)
.\src\lab9\lab9.py:582:80: E501 line too long (83 > 79 characters)
.\src\lab9\lab9.py:589:1: E302 expected 2 blank lines, found 1
.\src\lab9\lab9.py:589:80: E501 line too long (81 > 79 characters)
.\src\lab9\lab9.py:590:80: E501 line too long (84 > 79 characters)
.\src\lab9\lab9.py:654:80: E501 line too long (82 > 79 characters)
```

## Dataset
- **Dataset name:** Laptop Specs and Price Dataset
- **Dataset link:** https://www.kaggle.com/datasets/nabihazahid/laptop-details-dataset
- **Description:** The dataset contains laptop specification and price information.
