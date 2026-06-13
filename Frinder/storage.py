from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload

from db import session
from db_models import (
    FavoriteRecipeRow,
    RecipeIngredientRow,
    RecipeRow,
    ShoppingListRow,
    UserIngredientRow,
    IngredientRow
)
from models import Recipe
from seed import get_or_create_ingredient
from utils import clean_ingredient, recipe_key


def _recipe_row_to_model(recipe_row):
    ingredients = [link.ingredient.name for link in recipe_row.recipe_ingredients]
    return Recipe(
        name=recipe_row.name,
        ingredients=ingredients,
        instructions=recipe_row.instructions,
        cooking_time=recipe_row.cooking_time,
        difficulty=recipe_row.difficulty,
    )


def _recipe_id_by_key(session, target_key):
    return session.scalar(
        select(RecipeRow.id).where(func.lower(func.trim(RecipeRow.name)) == target_key)
    )


def _unique_cleaned_items(items):
    unique_items = []
    seen = set()

    for item in items:
        cleaned = clean_ingredient(item)
        if cleaned and cleaned not in seen:
            unique_items.append(cleaned)
            seen.add(cleaned)

    return unique_items


def _read_user_ingredient_names(session):
    rows = session.execute(
        select(UserIngredientRow)
        .options(selectinload(UserIngredientRow.ingredient))
        .order_by(UserIngredientRow.id)
    ).scalars().all()

    return [row.ingredient.name for row in rows]


def _read_shopping_list_names(session):
    rows = session.execute(
        select(ShoppingListRow)
        .options(selectinload(ShoppingListRow.ingredient))
        .order_by(ShoppingListRow.id)
    ).scalars().all()

    return [row.ingredient.name for row in rows]


def _read_favourite_recipe_names(session):
    rows = session.execute(
        select(FavoriteRecipeRow)
        .options(selectinload(FavoriteRecipeRow.recipe))
        .order_by(FavoriteRecipeRow.id)
    ).scalars().all()

    return [recipe_key(row.recipe.name) for row in rows]


def _run_write(action):
    with session() as db_session:
        action(db_session)
        db_session.commit()


def _run_read(action):
    with session() as db_session:
        return action(db_session)


def _replace_ingredient_rows(session, row_model, items):
    session.execute(delete(row_model))

    for item_name in _unique_cleaned_items(items):
        ingredient = get_or_create_ingredient(session, item_name)
        if ingredient is None:
            continue

        session.add(row_model(ingredient_id=ingredient.id))


def _store_favourite_recipe_rows(session, recipe_names, replace_all=False):
    if replace_all:
        _delete_favourite_recipe_rows(session)

    for recipe_name in recipe_names:
        recipe_id = _recipe_id_by_key(session, recipe_key(recipe_name))
        if recipe_id is None:
            continue

        _upsert_favourite_recipe_row(session, recipe_id)


def _upsert_favourite_recipe_row(session, recipe_id):
    existing = session.scalar(
        select(FavoriteRecipeRow).where(FavoriteRecipeRow.recipe_id == recipe_id)
    )
    if existing is None:
        session.add(FavoriteRecipeRow(recipe_id=recipe_id))


def _delete_favourite_recipe_rows(session, recipe_id=None):
    statement = delete(FavoriteRecipeRow)
    if recipe_id is not None:
        statement = statement.where(FavoriteRecipeRow.recipe_id == recipe_id)

    session.execute(statement)


def load_recipes():
    def action(db_session):
        recipe_rows = db_session.execute(
            select(RecipeRow)
            .options(
                selectinload(RecipeRow.recipe_ingredients).selectinload(
                    RecipeIngredientRow.ingredient
                )
            )
            .order_by(RecipeRow.id)
        ).scalars().all()

        return [_recipe_row_to_model(recipe_row) for recipe_row in recipe_rows]

    return _run_read(action)


def save_user_ingredients(ingredients):
    def action(db_session):
        _replace_ingredient_rows(db_session, UserIngredientRow, ingredients)

    _run_write(action)


def add_user_ingredient(ingredient):
    def action(db_session):
        cleaned_ingredient = clean_ingredient(ingredient)
        if not cleaned_ingredient:
            return

        ingredient_row = get_or_create_ingredient(db_session, cleaned_ingredient)
        if ingredient_row is None:
            return

        existing = db_session.scalar(
            select(UserIngredientRow).where(
                UserIngredientRow.ingredient_id == ingredient_row.id
            )
        )
        if existing is None:
            db_session.add(UserIngredientRow(ingredient_id=ingredient_row.id))

    _run_write(action)


def read_user_ingredients():
    return _run_read(_read_user_ingredient_names)


def read_shopping_list():
    return _run_read(_read_shopping_list_names)


def save_shopping_list(items):
    def action(db_session):
        _replace_ingredient_rows(db_session, ShoppingListRow, items)

    _run_write(action)


def read_favourite_recipe_names():
    return _run_read(_read_favourite_recipe_names)


def save_favourite_recipe_names(recipe_names):
    def action(db_session):
        _store_favourite_recipe_rows(db_session, recipe_names, replace_all=True)

    _run_write(action)


def add_favourite_recipe(recipe_name):
    def action(db_session):
        _store_favourite_recipe_rows(db_session, [recipe_name])

    _run_write(action)


def remove_favourite_recipe(recipe_name):
    def action(db_session):
        recipe_id = _recipe_id_by_key(db_session, recipe_key(recipe_name))
        if recipe_id is None:
            return

        _delete_favourite_recipe_rows(db_session, recipe_id)

    _run_write(action)


def add_missing_to_shopping_list(missing_items):
    save_shopping_list(read_shopping_list() + _unique_cleaned_items(missing_items))


def remove_from_shopping_list(item):
    item_to_remove = clean_ingredient(item)
    current_items = read_shopping_list()

    updated_items = [
        ingredient
        for ingredient in current_items
        if ingredient != item_to_remove
    ]

    save_shopping_list(updated_items)


def build_shopping_report(shopping_items, matched_recipes):
    if not shopping_items:
        return "Shopping list is empty."

    return "\n".join(f"- {item}" for item in shopping_items)


def remove_user_ingredient(ingredient):
    def action(db_session):
        item_to_remove = clean_ingredient(ingredient)
        if not item_to_remove:
            return

        ingredient_row = db_session.scalar(
            select(IngredientRow).where(IngredientRow.name == item_to_remove)
        )
        
        if ingredient_row is None:
            return

        db_session.execute(
            delete(UserIngredientRow).where(
                UserIngredientRow.ingredient_id == ingredient_row.id
            )
        )

    _run_write(action)