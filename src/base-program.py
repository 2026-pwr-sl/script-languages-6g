team_name = "6g"
team_members = [
    "Lucjan Pucelak",
    "Szymon Lisowski",
    "Efran Fernandez",
    "Oskar Nowakowski"]


def count_team_members(team_members):
    return len(team_members)
  
# This function returns a formatted greeting message for a given name.
def formatGreeting(name):
    return f" Welcome, {name}!"
 
def display_team_members(team_members):
    print("=" * 40)
    print(f"Team Name: {team_name}")
    print("=" * 40)
    print("\nTeam Members:")
    for i, member in enumerate(team_members, start=1):
        print(f"  {i}. {member}")

    print("\nProject is running correctly!")
    print("=" * 40)


print("\nGreetings:")

for member in team_members:

    print(formatGreeting(member))


print("\n Project is running correctly!")

if __name__ == '__main__':
    display_team_members(team_members)