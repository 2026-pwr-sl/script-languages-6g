import json
from pathlib import Path

from sqlalchemy import delete, select

from db_models import FavoriteRecipeRow, IngredientRow, RecipeIngredientRow, RecipeRow
from models import Recipe
from utils import clean_ingredient

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECIPES_FILE = DATA_DIR / "recipes.json"


def get_or_create_ingredient(session, ingredient_name):
    cleaned_name = clean_ingredient(ingredient_name)
    if not cleaned_name:
        return None

    ingredient = session.scalar(
        select(IngredientRow).where(IngredientRow.name == cleaned_name)
    )
    if ingredient is None:
        ingredient = IngredientRow(name=cleaned_name)
        session.add(ingredient)
        session.flush()

    return ingredient


def replace_recipes_from_json(session):
    session.execute(delete(FavoriteRecipeRow))
    session.execute(delete(RecipeIngredientRow))
    session.execute(delete(RecipeRow))

    if not RECIPES_FILE.exists():
        session.commit()
        return

    try:
        legacy_recipes = json.loads(RECIPES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        session.commit()
        return

    for legacy_recipe in legacy_recipes:
        recipe = Recipe.from_dict(legacy_recipe)
        recipe_row = RecipeRow(
            name=recipe.name,
            instructions=recipe.instructions,
            cooking_time=recipe.cooking_time,
            difficulty=recipe.difficulty,
        )
        session.add(recipe_row)
        session.flush()

        for position, ingredient_name in enumerate(recipe.ingredients):
            ingredient = get_or_create_ingredient(session, ingredient_name)
            if ingredient is None:
                continue

            session.add(
                RecipeIngredientRow(
                    recipe_id=recipe_row.id,
                    ingredient_id=ingredient.id,
                    position=position,
                )
            )

    session.commit()
