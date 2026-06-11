from dataclasses import replace

from models import Recipe
from utils import clean_ingredient


def match_recipes(user_ingredients, recipes):
    user_set = set(user_ingredients)
    matches = []

    for recipe in recipes:
        if not isinstance(recipe, Recipe):
            recipe = Recipe.from_dict(recipe)

        recipe_ingredients = [clean_ingredient(i) for i in recipe.ingredients]
        available = [i for i in recipe_ingredients if i in user_set]
        missing = [i for i in recipe_ingredients if i not in user_set]
        score = round((len(available) / len(recipe_ingredients)) * 100, 2) if recipe_ingredients else 0

        matches.append(
            replace(
                recipe,
                ingredients=recipe_ingredients,
                available_ingredients=available,
                missing_ingredients=missing,
                match_score=score,
            )
        )

    return sorted(matches, key=lambda x: x.match_score, reverse=True)
