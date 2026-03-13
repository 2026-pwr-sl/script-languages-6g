import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from base_program import format_greeting, count_team_members

def run_tests():
    test_members = ["Lucjan Pucelak", "Szymon Lisowski", "Efran Fernandez", "Oskar Nowakowski"]

    # 1 Test for format_greeting function
    greeting = format_greeting("Oskar")
    if "Welcome" in greeting and "Oskar" in greeting:
        print("\nformat_greeting passed.")
    else:
        print("\nformat_greeting failed.")

    # 2. Normal case for count_team_members
    if count_team_members(test_members) == 4:
        print("count_team_members normal case passed.")
    else:
        print("count_team_members normal case failed.")

if __name__ == "__main__":
    run_tests()
