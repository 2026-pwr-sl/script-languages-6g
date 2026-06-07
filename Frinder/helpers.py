import json
from pathlib import Path

import pandas as pd


def clean_ingredient(value):
    return str(value).strip().lower()


def parse_ingredients(raw_text):
    if not raw_text:
        return []
    items = raw_text.replace("\n", ",").split(",")
    return [clean_ingredient(item) for item in items if clean_ingredient(item)]


def load_recipes(filepath):
    path = Path(filepath)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_user_ingredients(ingredients, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(ingredients), encoding="utf-8")


def match_recipes(user_ingredients, recipes):
    user_set = set(user_ingredients)
    matches = []

    for recipe in recipes:
        recipe_ingredients = [clean_ingredient(i) for i in recipe.get("ingredients", [])]
        available = [i for i in recipe_ingredients if i in user_set]
        missing = [i for i in recipe_ingredients if i not in user_set]
        score = round((len(available) / len(recipe_ingredients)) * 100, 2) if recipe_ingredients else 0

        matches.append(
            {
                "name": recipe.get("name", "Unknown"),
                "available_ingredients": available,
                "missing_ingredients": missing,
                "match_score": score,
                "instructions": recipe.get("instructions", ""),
                "cooking_time": recipe.get("cooking_time", 0),
                "difficulty": recipe.get("difficulty", "Easy"),
            }
        )

    return sorted(matches, key=lambda x: x["match_score"], reverse=True)


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