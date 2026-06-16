from dataclasses import replace

from models import Recipe
from utils import clean_ingredient


DIETARY_RESTRICTION_OPTIONS = [
    {"value": "vegetarian", "label": "Vegetarian"},
    {"value": "vegan", "label": "Vegan"},
    {"value": "dairy-free", "label": "Dairy-free"},
    {"value": "gluten-free", "label": "Gluten-free"},
    {"value": "egg-free", "label": "Egg-free"},
    {"value": "nut-free", "label": "Nut-free"},
]

DIETARY_RESTRICTION_LABELS = {
    option["value"]: option["label"]
    for option in DIETARY_RESTRICTION_OPTIONS
}

DIETARY_RESTRICTION_CONFLICTS = {
    "vegetarian": {
        "bacon",
        "beef",
        "broth",
        "chicken",
        "fish",
        "ham",
        "meat",
        "meatballs",
        "pork",
        "salmon",
        "sausage",
        "sausages",
        "shrimp",
        "sour cream",
        "trout",
        "tuna",
        "turkey",
        "anchovies",
        "lard",
    },
    "vegan": {
        "bacon",
        "beef",
        "broth",
        "butter",
        "caesar dressing",
        "cheese",
        "chicken",
        "cream",
        "cream cheese",
        "eggs",
        "fish",
        "feta",
        "ham",
        "honey",
        "lamb",
        "mayonnaise",
        "meat",
        "meatballs",
        "milk",
        "mozzarella",
        "parmesan",
        "pork",
        "salmon",
        "sausage",
        "sausages",
        "shrimp",
        "sour cream",
        "trout",
        "tuna",
        "turkey",
        "yogurt",
        "lard",
        "gelatin",
        "worcestershire sauce",
        "anchovies",
    },
    "dairy-free": {"butter", "cheese", "cream", "milk", "yogurt", "cream cheese", "feta", "mozzarella", "parmesan", "sour cream"},
    "gluten-free": {"bread", "flour", "pasta", "roll", "wheat", "bagel", "buns", "flatbread", "lasagna sheets", "macaroni", "noodles", "spaghetti", "tortilla"},
    "egg-free": {"egg", "eggs"},
    "nut-free": {
        "almond",
        "almonds",
        "cashew",
        "cashews",
        "hazelnut",
        "hazelnuts",
        "peanut",
        "peanut butter",
        "peanuts",
        "pecan",
        "pecans",
        "walnut",
        "walnuts",
    },
}


def normalize_dietary_restrictions(dietary_restrictions):
    selected_restrictions = []
    seen = set()

    for restriction in dietary_restrictions or []:
        restriction_key = clean_ingredient(restriction)

        if (
            restriction_key in DIETARY_RESTRICTION_LABELS
            and restriction_key not in seen
        ):
            selected_restrictions.append(restriction_key)
            seen.add(restriction_key)

    return selected_restrictions


def dietary_restriction_labels(dietary_restrictions):
    return [
        DIETARY_RESTRICTION_LABELS[restriction]
        for restriction in normalize_dietary_restrictions(dietary_restrictions)
    ]


def restricted_ingredients_for(dietary_restrictions):
    restricted_ingredients = set()

    for restriction in normalize_dietary_restrictions(dietary_restrictions):
        restricted_ingredients.update(DIETARY_RESTRICTION_CONFLICTS[restriction])

    return restricted_ingredients


def ingredient_name_variants(ingredient):
    cleaned_ingredient = clean_ingredient(ingredient)
    if not cleaned_ingredient:
        return set()

    variants = {cleaned_ingredient}

    if cleaned_ingredient.endswith("s"):
        variants.add(cleaned_ingredient[:-1])
    else:
        variants.add(f"{cleaned_ingredient}s")

    return variants


def expanded_ingredient_set(ingredients):
    expanded_ingredients = set()

    for ingredient in ingredients or []:
        expanded_ingredients.update(ingredient_name_variants(ingredient))

    return expanded_ingredients


def recipe_conflicts_with_preferences(
    recipe,
    dietary_restrictions=None,
    excluded_ingredients=None,
):
    recipe_ingredients = {clean_ingredient(i) for i in recipe.ingredients}
    excluded_set = expanded_ingredient_set(excluded_ingredients)
    restriction_conflicts = expanded_ingredient_set(
        restricted_ingredients_for(dietary_restrictions)
    )

    return bool(recipe_ingredients & (excluded_set | restriction_conflicts))


def filter_recipes_for_preferences(
    recipes,
    dietary_restrictions=None,
    excluded_ingredients=None,
):
    filtered_recipes = []

    for recipe in recipes:
        if not isinstance(recipe, Recipe):
            recipe = Recipe.from_dict(recipe)

        if not recipe_conflicts_with_preferences(
            recipe,
            dietary_restrictions=dietary_restrictions,
            excluded_ingredients=excluded_ingredients,
        ):
            filtered_recipes.append(recipe)

    return filtered_recipes


def match_recipes(
    user_ingredients,
    recipes,
    dietary_restrictions=None,
    excluded_ingredients=None,
):
    user_set = set(user_ingredients)
    matches = []

    for recipe in filter_recipes_for_preferences(
        recipes,
        dietary_restrictions=dietary_restrictions,
        excluded_ingredients=excluded_ingredients,
    ):
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
