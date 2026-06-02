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