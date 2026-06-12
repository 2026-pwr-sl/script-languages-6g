from db import session
from seed import replace_recipes_from_json
from storage import read_favourite_recipe_names, save_favourite_recipe_names


def main():
    favourite_recipe_names = read_favourite_recipe_names()

    with session() as db_session:
        replace_recipes_from_json(db_session)

    if favourite_recipe_names:
        save_favourite_recipe_names(favourite_recipe_names)

    print("Recipes imported from data/recipes.json.")
    if favourite_recipe_names:
        print(f"Restored {len(favourite_recipe_names)} favourite recipe(s).")


if __name__ == "__main__":
    main()
