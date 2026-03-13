team_name = "6g"
team_members = [
    "Lucjan Pucelak",
    "Szymon Lisowski",
    "Efran Fernandez",
    "Oskar Nowakowski"]


def count_team_members(team_members):
    return len(team_members)
  
# This function returns a formatted greeting message for a given name.
def format_greeting(name):
    return f" Welcome, {name}!"

def greet_team(team_members):
    print("\nGreetings:")
    for member in team_members:
        print(format_greeting(member))
 
def display_team_members(team_members):
    print("=" * 40)
    print(f"Team Name: {team_name}")
    print("=" * 40)
    print("\nTeam Members:")
    for i, member in enumerate(team_members, start=1):
        print(f"  {i}. {member}")
    print(f"\nNumber of members: {count_team_members(team_members)}")
    greet_team(team_members)
    print("\nProject is running correctly!")
    print("=" * 40)

if __name__ == '__main__':
    display_team_members(team_members)
