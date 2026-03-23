import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from utils import format_greeting
from team import count_team_members, team_data


def run_tests():

    # 1 Test for format_greeting function
    greeting = format_greeting("Oskar")
    if "Welcome" in greeting and "Oskar" in greeting:
        print("\nformat_greeting passed.")
    else:
        print("\nformat_greeting failed.")

    # 2. Normal case for count_team_members
    if count_team_members(team_data) == 4:
        print("count_team_members normal case passed.")
    else:
        print("count_team_members normal case failed.")

if __name__ == "__main__":
    run_tests()
