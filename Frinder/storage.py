import json
from pathlib import Path

from models import Recipe
from utils import clean_ingredient, recipe_key


def load_recipes(filepath):
    path = Path(filepath)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return [Recipe.from_dict(recipe) for recipe in json.load(file)]


def save_user_ingredients(ingredients, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(ingredients), encoding="utf-8")


def read_user_ingredients(filepath):
    path = Path(filepath)

    if not path.exists():
        return []

    return [
        clean_ingredient(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if clean_ingredient(line)
    ]


def read_shopping_list(filepath):
    path = Path(filepath)

    if not path.exists():
        return []

    return [
        clean_ingredient(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if clean_ingredient(line)
    ]


def save_shopping_list(items, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    unique_items = sorted(set(clean_ingredient(item) for item in items if clean_ingredient(item)))
    path.write_text("\n".join(unique_items), encoding="utf-8")


def read_favourite_recipe_names(filepath):
    path = Path(filepath)

    if not path.exists():
        return []

    return [
        recipe_key(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if recipe_key(line)
    ]


def save_favourite_recipe_names(recipe_names, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    unique_recipe_names = []
    seen_names = set()

    for recipe_name in recipe_names:
        name = recipe_key(recipe_name)

        if name and name not in seen_names:
            unique_recipe_names.append(name)
            seen_names.add(name)

    path.write_text("\n".join(unique_recipe_names), encoding="utf-8")


def add_favourite_recipe(recipe_name, filepath):
    favourite_names = read_favourite_recipe_names(filepath)
    favourite_names.append(recipe_name)
    save_favourite_recipe_names(favourite_names, filepath)


def remove_favourite_recipe(recipe_name, filepath):
    name_to_remove = recipe_key(recipe_name)
    favourite_names = [
        name
        for name in read_favourite_recipe_names(filepath)
        if name != name_to_remove
    ]

    save_favourite_recipe_names(favourite_names, filepath)


def add_missing_to_shopping_list(missing_items, filepath):
    current_items = read_shopping_list(filepath)
    new_items = [
        clean_ingredient(item)
        for item in missing_items
        if clean_ingredient(item)
    ]

    save_shopping_list(current_items + new_items, filepath)


def remove_from_shopping_list(item, filepath):
    item_to_remove = clean_ingredient(item)
    current_items = read_shopping_list(filepath)

    updated_items = [
        ingredient
        for ingredient in current_items
        if ingredient != item_to_remove
    ]

    save_shopping_list(updated_items, filepath)


def build_shopping_report(shopping_items, matched_recipes):
    if not shopping_items:
        return "Shopping list is empty."

    return "\n".join(f"- {item}" for item in shopping_items)
