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


def add_member(team, name):
    team["members"].append({"name": name})


def search_member(team, name):
    for member in team["members"]:
        if member["name"] == name:
            return member
    return None