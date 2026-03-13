import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from base_program import format_greeting

def run_tests():
    test_members = ["Lucjan Pucelak", "Szymon Lisowski", "Efran Fernandez", "Oskar Nowakowski"]

    # 1 Test for format_greeting function
    greeting = format_greeting("Oskar")
    if "Welcome" in greeting and "Oskar" in greeting:
        print("\nformat_greeting passed.")
    else:
        print("\nformat_greeting failed.")

if __name__ == "__main__":
    run_tests()