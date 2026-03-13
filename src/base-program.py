team_name = "6g"

team_members = [

    "Lucian Pucelak",

    "Szymon Lisowski",

    "Efran Fernandz",
    
    "Oskar Nowakowski"

]

# This function returns a formatted greeting message for a given name.
def formatGreeting(name):
    return f" Welcome, {name}!"


print("=" * 40)

print(f"Team Name: {team_name}")

print("=" * 40)


print("\nTeam Members:")

for i, member in enumerate(team_members, start=1):

    print(f"  {i}. {member}")


print("\nGreetings:")

for member in team_members:

    print(formatGreeting(member))


print("\n Project is running correctly!")

print("=" * 40)