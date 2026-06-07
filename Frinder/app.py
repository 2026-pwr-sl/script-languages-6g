from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, url_for

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
    return render_template("summary.html")


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