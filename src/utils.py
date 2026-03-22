def format_greeting(name):
    return f" Welcome, {name}!"


def greet_team(team_members):
    print("\nGreetings:")
    for member in team_members:
        print(format_greeting(member))