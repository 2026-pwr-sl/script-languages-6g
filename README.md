# Script Languages – Group 6g

## Group Information

- **Group name:** 6g
- **Repository:** `script-languages-6g`

## Team Members

- Efran Fernandez Fernandez
- Szymon Lisowski
- Oskar Nowakowski
- Lucjan Pucelak

## Project Goal

The goal of this project is to learn the basics of teamwork with Python and GitHub. The repository is used to practice collaboration, branches, commits, pull requests, and the development of a simple Python program as a team.

## Project Structure

- `src/` – source code
- `tests/` – tests
- `docs/` – documentation or notes
- `data/` – optional input data

## Instructions For Running The Program

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

## Lab10 Environment Variables

The Lab10 CSV analysis uses environment variables loaded from a `.env` file with the `python-dotenv` module.

Used variables:

- `LAB10_STAT_CATEGORY` – selects the product category used for the average purchase amount statistic. Use `ALL` to include every category.
- `LAB10_MIN_QUANTITY` – selects the minimum quantity required for a record to be included in the average purchase amount statistic.

Example `.env` file:

```env
LAB10_STAT_CATEGORY=ALL
LAB10_MIN_QUANTITY=1
```

Run Lab10 without Excel output:

```bash
python3 src/lab10.py data/black_friday_sales_100k.csv
```

Run Lab10 with Excel output:

```bash
python3 src/lab10.py data/black_friday_sales_100k.csv -o report.xlsx
```

## Team Work Summary

### Who Was Responsible For What

- Lucjan Pucelak – repository setup, responsibility dividing, documentation, tests
- Efran Fernandez Fernandez – program development and functions
- Szymon Lisowski – repository managing, code review, maintenance, refactoring
- Oskar Nowakowski – project structure setup, code development support, tests

### Problems We Encountered

- GitHub authentication and pushing changes from local branches
- Working on separate branches and keeping them updated
- Matching issue descriptions with the current function names in the code
- Learning how to create pull requests and respond to review comments

### What We Learned While Working With Python And GitHub

- How to organize a simple Python project into folders such as `src`, `tests`, and `docs`
- How to run a Python program locally
- How to prepare simple tests for Python functions
- How to use GitHub Issues, branches, commits, and pull requests
- How code review works and why clear branch names and commit messages are important
- How to resolve merging conflicts
- How to collaborate and build a project together