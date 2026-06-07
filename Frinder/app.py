from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, url_for

from collections import Counter

from helpers import (
    add_missing_to_shopping_list,
    build_shopping_report,
    load_recipes,
    match_recipes,
    parse_ingredients,
    read_shopping_list,
    read_user_ingredients,
    remove_from_shopping_list,
    save_user_ingredients,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECIPES_FILE = DATA_DIR / "recipes.json"
USER_INGREDIENTS_FILE = DATA_DIR / "user_ingredients.txt"
SHOPPING_LIST_FILE = DATA_DIR / "shopping_list.txt"

app = Flask(__name__)
app.secret_key = "frinder2137glhfdonthackmeplease"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    if request.method == "POST":
        user_ingredients = parse_ingredients(request.form.get("ingredients", ""))

        if not user_ingredients:
            flash("Please enter at least one ingredient.", "error")
            return redirect(url_for("index"))

        save_user_ingredients(user_ingredients, USER_INGREDIENTS_FILE)
        recipes_list = load_recipes(RECIPES_FILE)
        suggestions = match_recipes(user_ingredients, recipes_list)

        return render_template(
            "recipes.html",
            user_ingredients=user_ingredients,
            suggestions=suggestions,
        )
    return render_template("recipes.html", user_ingredients=[], suggestions=[])


@app.route("/all-recipes")
def all_recipes():
    recipes_list = load_recipes(RECIPES_FILE)
    return render_template("all_recipes.html", recipes=recipes_list)

        
@app.route("/summary")
def summary():
    recipes_list = load_recipes(RECIPES_FILE)
    user_ingredients = read_user_ingredients(USER_INGREDIENTS_FILE)

    if not user_ingredients:
        return render_template("summary.html", empty=True)

    suggestions = match_recipes(user_ingredients, recipes_list)
    
    total_available = len(user_ingredients)
    total_suggested = len(suggestions)
    
    scores = [s['match_score'] for s in suggestions] if suggestions else [0]
    best_match = max(scores) if suggestions else 0
    avg_match = sum(scores) / len(scores) if suggestions else 0

    missing_counter = Counter()
    for s in suggestions:
        for missing in s.get('missing_ingredients', []):
            missing_counter[missing.lower()] += 1

    most_common_missing = missing_counter.most_common(1)[0][0] if missing_counter else "None"
    missing_table_data = missing_counter.most_common(5)

    if best_match == 0:
        recommendation = "Your fridge is bare."
    elif best_match < 20:
        recommendation = "You should go shopping."
    elif best_match < 60:
        recommendation = "Decent matches available."
    else:
        recommendation = "You can cook a full meal right now without shopping."


    return render_template(
        "summary.html",
        empty=False,
        total_available=total_available,
        total_suggested=total_suggested,
        best_match=round(best_match, 1),
        avg_match=round(avg_match, 1),
        most_common_missing=most_common_missing.capitalize(),
        recommendation=recommendation,
        missing_table_data=missing_table_data,
    )


@app.route("/favourites")
def favourites():
    return render_template("favourites.html")


def get_latest_recipe_matches():
    user_ingredients = read_user_ingredients(USER_INGREDIENTS_FILE)

    if not user_ingredients:
        return []

    recipes_list = load_recipes(RECIPES_FILE)
    suggestions = match_recipes(user_ingredients, recipes_list)

    return [
        recipe
        for recipe in suggestions
        if recipe.get("match_score", 0) > 0
    ]


@app.route("/shopping-list")
def shopping_list():
    shopping_items = read_shopping_list(SHOPPING_LIST_FILE)
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
    add_missing_to_shopping_list(missing_items, SHOPPING_LIST_FILE)

    return redirect(request.referrer or url_for("shopping_list"))


@app.route("/shopping-list/remove", methods=["POST"])
def remove_shopping_item():
    ingredient = request.form.get("ingredient", "")
    remove_from_shopping_list(ingredient, SHOPPING_LIST_FILE)

    flash(f"{ingredient} removed from shopping list.", "success")
    return redirect(url_for("shopping_list"))


@app.route("/shopping-list/download")
def download_shopping_list():
    shopping_items = read_shopping_list(SHOPPING_LIST_FILE)
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