team_name = "6g"
team_members = [
    "Lucjan Pucelak",
    "Szymon Lisowski",
    "Efran Fernandez",
    "Oskar Nowakowski"]


def count_team_members(team_members):
    return len(team_members)

def display_team_members(team_members):
    print("=" * 40)
    print(f"Team Name: {team_name}")
    print("=" * 40)
    print("\nTeam Members:")
    for i, member in enumerate(team_members, start=1):
        print(f"  {i}. {member}")

    print("\nProject is running correctly!")
    print("=" * 40)



if __name__ == '__main__':
    display_team_members(team_members)