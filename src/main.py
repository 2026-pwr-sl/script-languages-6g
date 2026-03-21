from team import team_members, display_team_members
from utils import greet_team


def main():
    display_team_members(team_members)
    greet_team(team_members)


if __name__ == "__main__":
    main()