from pathlib import Path

import json

from flask import Flask, Response, flash, redirect, render_template, request, url_for

from collections import Counter

from charts import generate_summary_graphs
from matching import match_recipes
from storage import (
    add_favourite_recipe,
    add_missing_to_shopping_list,
    add_user_ingredient,
    build_shopping_report,
    load_recipes,
    read_favourite_recipe_names,
    read_shopping_list,
    read_user_ingredients,
    recipe_key,
    remove_favourite_recipe,
    remove_from_shopping_list,
    remove_user_ingredient,
    save_user_ingredients,
)
from utils import parse_ingredients

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "match_history.json"

app = Flask(__name__)
app.secret_key = "frinder2137glhfdonthackmeplease"


def read_uploaded_ingredients_file(uploaded_file):
    if not uploaded_file or not uploaded_file.filename:
        return ""

    if not uploaded_file.filename.lower().endswith(".txt"):
        raise ValueError("Please upload a .txt file with your ingredients.")

    try:
        return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Please upload a valid UTF-8 .txt file.") from error


def add_favourite_status(recipes, favourite_recipe_names):
    favourite_name_set = set(favourite_recipe_names)

    return [
        recipe.__class__(
            **{
                **recipe.to_dict(),
                "is_favourite": recipe_key(recipe.name) in favourite_name_set,
            }
        )
        for recipe in recipes
    ]


def get_recipes_with_favourite_status():
    recipes_list = load_recipes()
    favourite_recipe_names = read_favourite_recipe_names()

    return add_favourite_status(recipes_list, favourite_recipe_names), favourite_recipe_names


def get_recipe_suggestions(user_ingredients):
    recipes_list = load_recipes()
    favourite_recipe_names = read_favourite_recipe_names()
    raw_suggestions = match_recipes(user_ingredients, recipes_list)
    
    save_match_history(user_ingredients, raw_suggestions)
    
    suggestions = add_favourite_status(
        raw_suggestions,
        favourite_recipe_names,
    )

    return suggestions, favourite_recipe_names


@app.route("/quick-add", methods=["POST"])
def quick_add():
    ingredient = request.form.get("ingredient")

    if ingredient:
        add_user_ingredient(ingredient)
        flash(f"Added {ingredient} to your fridge!", "success")

    return redirect(url_for("index", open_widget=True))


@app.route("/")
def index():
    saved_items = read_user_ingredients()

    saved_items_str = ", ".join(saved_items)

    return render_template("index.html", saved_items_str=saved_items_str)


@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    if request.method == "POST":
        ingredients_text = request.form.get("ingredients", "")
        uploaded_file = request.files.get("ingredients_file")

        try:
            uploaded_ingredients_text = read_uploaded_ingredients_file(uploaded_file)
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("index"))

        user_ingredients = parse_ingredients(
            f"{ingredients_text}\n{uploaded_ingredients_text}"
        )

        if not user_ingredients:
            flash("Please enter or upload at least one ingredient.", "error")
            return redirect(url_for("index"))

        save_user_ingredients(user_ingredients)
        suggestions, favourite_recipe_names = get_recipe_suggestions(user_ingredients)

        return render_template(
            "recipes.html",
            user_ingredients=user_ingredients,
            suggestions=suggestions,
            favourite_recipe_names=favourite_recipe_names,
        )

    user_ingredients = read_user_ingredients()
    favourite_recipe_names = read_favourite_recipe_names()
    suggestions = []

    if user_ingredients:
        suggestions, favourite_recipe_names = get_recipe_suggestions(user_ingredients)

    return render_template(
        "recipes.html",
        user_ingredients=user_ingredients,
        suggestions=suggestions,
        favourite_recipe_names=favourite_recipe_names,
    )
    

@app.route("/remove-ingredient", methods=["POST"])
def remove_ingredient():
    ingredient = request.form.get("ingredient")
    if ingredient:
        remove_user_ingredient(ingredient)
        
    return redirect(url_for("recipes"))


@app.route("/all-recipes")
def all_recipes():
    recipes_list, favourite_recipe_names = get_recipes_with_favourite_status()

    return render_template(
        "all_recipes.html",
        recipes=recipes_list,
        favourite_recipe_names=favourite_recipe_names,
    )


@app.route("/summary")
def summary():
    user_ingredients = read_user_ingredients()

    if not user_ingredients or not HISTORY_FILE.exists():
        return render_template("summary.html", empty=True)

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    filename_missing = "summary_missing.png"
    filename_difficulty = "summary_difficulty.png"

    return render_template(
        "summary.html",
        empty=False,
        total_available=data.get("total_available", 0),
        total_suggested=data.get("total_suggested", 0),
        best_match=data.get("best_match", 0),
        avg_match=data.get("avg_match", 0),
        most_common_missing=data.get("most_common_missing", "None"),
        recommendation=data.get("recommendation", ""),
        missing_table_data=data.get("missing_table_data", []),
        graph_missing_url=url_for('static', filename=filename_missing),
        graph_difficulty_url=url_for('static', filename=filename_difficulty)
    )
    

def save_match_history(user_ingredients, suggestions):
    if not user_ingredients:
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        return

    match_scores = [s.match_score for s in suggestions]
    best_match = max(match_scores, default=0)
    avg_match = sum(match_scores) / len(match_scores) if match_scores else 0

    missing_counter = Counter()
    for suggestion in suggestions:
        for missing in suggestion.missing_ingredients:
            missing_counter[missing.lower()] += 1

    most_common_missing = missing_counter.most_common(1)[0][0] if missing_counter else "None"
    missing_table_data = missing_counter.most_common(10)

    if best_match == 0:
        recommendation = "Your fridge is empty."
    elif best_match < 20:
        recommendation = "You should go shopping."
    elif best_match < 60:
        recommendation = "Decent matches available."
    else:
        recommendation = "You can cook a full meal right now without shopping."

    history_data = {
        "total_available": len(user_ingredients),
        "total_suggested": len(suggestions),
        "best_match": round(best_match, 1),
        "avg_match": round(avg_match, 1),
        "most_common_missing": most_common_missing.capitalize(),
        "recommendation": recommendation,
        "missing_table_data": missing_table_data
    }

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f)

    filename_missing = "summary_missing.png"
    filename_difficulty = "summary_difficulty.png"
    
    generate_summary_graphs(
        missing_counter, 
        suggestions, 
        BASE_DIR / "static" / filename_missing, 
        BASE_DIR / "static" / filename_difficulty
    )


@app.route("/favourites")
def favourites():
    recipes_list, favourite_recipe_names = get_recipes_with_favourite_status()
    favourite_recipes = [
        recipe
        for recipe in recipes_list
        if recipe_key(recipe.name) in favourite_recipe_names
    ]

    return render_template(
        "favourites.html",
        recipes=favourite_recipes,
        favourite_recipe_names=favourite_recipe_names,
    )


@app.route("/favourites/add", methods=["POST"])
def add_to_favourites():
    recipe_name = request.form.get("recipe_name", "")

    if not recipe_key(recipe_name):
        flash("Recipe could not be added to favourites.", "error")
    else:
        add_favourite_recipe(recipe_name)
        flash(f"{recipe_name} added to favourites.", "success")

    return redirect(request.referrer or url_for("favourites"))


@app.route("/favourites/remove", methods=["POST"])
def remove_from_favourites():
    recipe_name = request.form.get("recipe_name", "")

    if not recipe_key(recipe_name):
        flash("Recipe could not be removed from favourites.", "error")
    else:
        remove_favourite_recipe(recipe_name)
        flash(f"{recipe_name} removed from favourites.", "success")

    return redirect(request.referrer or url_for("favourites"))


def get_latest_recipe_matches():
    user_ingredients = read_user_ingredients()

    if not user_ingredients:
        return []

    recipes_list = load_recipes()
    suggestions = match_recipes(user_ingredients, recipes_list)

    return [
        recipe
        for recipe in suggestions
        if recipe.match_score > 0
    ]


@app.route("/shopping-list")
def shopping_list():
    shopping_items = read_shopping_list()
    matched_recipes = get_latest_recipe_matches()
    report_text = build_shopping_report(shopping_items, matched_recipes)

    return render_template(
        "shopping_list.html",
        shopping_items=shopping_items,
        matched_recipes=matched_recipes,
        report_text=report_text,
    )


@app.route("/shopping-list/add", methods=["POST"])
def add_to_shopping_list():
    missing_items = request.form.getlist("missing_ingredients")
    add_missing_to_shopping_list(missing_items)

    return redirect(request.referrer or url_for("shopping_list"))


@app.route("/shopping-list/remove", methods=["POST"])
def remove_shopping_item():
    ingredient = request.form.get("ingredient", "")
    remove_from_shopping_list(ingredient)

    flash(f"{ingredient} removed from shopping list.", "success")
    return redirect(url_for("shopping_list"))


@app.route("/shopping-list/download")
def download_shopping_list():
    shopping_items = read_shopping_list()
    matched_recipes = get_latest_recipe_matches()
    report_text = build_shopping_report(shopping_items, matched_recipes)

    return Response(
        report_text,
        mimetype="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=shopping_list.txt"
        },
    )


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=True, port=5001)
