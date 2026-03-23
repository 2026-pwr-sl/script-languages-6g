import sys
import os
import json
import unittest
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from team import count_team_members, add_member, search_member, save_to_json
from utils import format_greeting


class TestTeamLogic(unittest.TestCase):
    def setUp(self):
        self.team = {
            "team_name": "6g",
            "members": [
                {"name": "Lucjan Pucelak"},
                {"name": "Szymon Lisowski"},
            ],
        }

    def test_format_greeting_returns_expected_text(self):
        self.assertEqual(format_greeting("Lucjan"), " Welcome, Lucjan!")

    def test_count_team_members_returns_correct_number(self):
        self.assertEqual(count_team_members(self.team), 2)

    def test_add_member_adds_new_member(self):
        add_member(self.team, "Oskar Nowakowski")
        self.assertEqual(len(self.team["members"]), 3)
        self.assertIn({"name": "Oskar Nowakowski"}, self.team["members"])

    def test_search_member_returns_existing_member(self):
        result = search_member(self.team, "Szymon Lisowski")
        self.assertEqual(result, {"name": "Szymon Lisowski"})

    def test_save_to_json_writes_correct_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "team_data.json")

            save_to_json(self.team, file_path)

            self.assertTrue(os.path.exists(file_path))

            with open(file_path, "r") as file:
                loaded_data = json.load(file)

            self.assertEqual(loaded_data, self.team)


if __name__ == "__main__":
    unittest.main()
