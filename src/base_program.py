team_data = {
    "team_name": "6g",
    "members": [
        {"name": "Lucian Pucelak"},
        {"name": "Szymon Lisowski"},
        {"name": "Efran Fernandz"},
        {"name": "Oskar Nowakowski"}
    ]
}

def count_team_members(team):
    return len(team["members"])


# This function returns a formatted greeting message for a given name.
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



def add_member(team, name):
    team["members"].append({"name": name})


def search_member(team, name):
    for member in team["members"]:
        if member["name"] == name:
            return member
    return None




if __name__ == '__main__':
    display_team_members(team_data)
