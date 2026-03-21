def format_greeting(name):
    return f" Welcome, {name}!"


def greet_team(team):
    print("\nGreetings:")
    for member in team["members"]:
        print(format_greeting(member["name"]))


def display_team_members(team):
    print("=" * 40)
    print(f"Team Name: {team['team_name']}")   
    print("=" * 40)
    print("\nTeam Members:")
    for i, member in enumerate(team["members"], start=1):
        print(f"  {i}. {member['name']}")

    print("\nProject is running correctly!")
    print("=" * 40)