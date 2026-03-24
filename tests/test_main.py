import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from main import main
from team import count_team_members, team_data
from utils import format_greeting


def assert_contains(output, expected, test_name):
    if expected in output:
        print(f"{test_name} passed.")
    else:
        print(f"{test_name} failed.")


def run_tests():
    greeting = format_greeting("Oskar")
    assert_contains(greeting, "Welcome, Oskar!", "format_greeting")

    if count_team_members(team_data) == 4:
        print("count_team_members passed.")
    else:
        print("count_team_members failed.")

    show_team_output = io.StringIO()
    with redirect_stdout(show_team_output):
        main(["--show-team"])
    assert_contains(
        show_team_output.getvalue(), "Team Name: 6g", "cli --show-team"
    )

    count_output = io.StringIO()
    with redirect_stdout(count_output):
        main(["--count"])
    assert_contains(
        count_output.getvalue(),
        "Number of team members: 4",
        "cli --count",
    )

    greet_output = io.StringIO()
    with redirect_stdout(greet_output):
        main(["--greet", "Efran"])
    assert_contains(
        greet_output.getvalue(), "Welcome, Efran!", "cli --greet"
    )

if __name__ == "__main__":
    run_tests()
