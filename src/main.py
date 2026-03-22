from team import team_data, save_to_json
from utils import greet_team, display_team_members


def main():
    greet_team(team_data)
    display_team_members(team_data)
    save_to_json(team_data, "data/team_data.json")


if __name__ == "__main__":
    main()
