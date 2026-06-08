from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, url_for

from collections import Counter

from helpers import (
    add_favourite_recipe,
    add_missing_to_shopping_list,
    build_shopping_report,
    load_recipes,
    match_recipes,
    parse_ingredients,
    read_favourite_recipe_names,
    read_shopping_list,
    read_user_ingredients,
    recipe_key,
    remove_favourite_recipe,
    remove_from_shopping_list,
    save_user_ingredients,
    generate_summary_graphs,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECIPES_FILE = DATA_DIR / "recipes.json"
USER_INGREDIENTS_FILE = DATA_DIR / "user_ingredients.txt"
SHOPPING_LIST_FILE = DATA_DIR / "shopping_list.txt"
FAVOURITES_FILE = DATA_DIR / "favourites.txt"

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
        {
            **recipe,
            "is_favourite": recipe_key(recipe.get("name", "")) in favourite_name_set,
        }
        for recipe in recipes
    ]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    favourite_recipe_names = read_favourite_recipe_names(FAVOURITES_FILE)

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

        save_user_ingredients(user_ingredients, USER_INGREDIENTS_FILE)
        recipes_list = load_recipes(RECIPES_FILE)
        suggestions = add_favourite_status(
            match_recipes(user_ingredients, recipes_list),
            favourite_recipe_names,
        )

        return render_template(
            "recipes.html",
            user_ingredients=user_ingredients,
            suggestions=suggestions,
            favourite_recipe_names=favourite_recipe_names,
        )

    user_ingredients = read_user_ingredients(USER_INGREDIENTS_FILE)
    suggestions = []

    if user_ingredients:
        recipes_list = load_recipes(RECIPES_FILE)
        suggestions = add_favourite_status(
            match_recipes(user_ingredients, recipes_list),
            favourite_recipe_names,
        )

    return render_template(
        "recipes.html",
        user_ingredients=user_ingredients,
        suggestions=suggestions,
        favourite_recipe_names=favourite_recipe_names,
    )


@app.route("/all-recipes")
def all_recipes():
    recipes_list = load_recipes(RECIPES_FILE)
    favourite_recipe_names = read_favourite_recipe_names(FAVOURITES_FILE)
    recipes_list = add_favourite_status(recipes_list, favourite_recipe_names)

    return render_template(
        "all_recipes.html",
        recipes=recipes_list,
        favourite_recipe_names=favourite_recipe_names,
    )

        
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

    filename_missing = "summary_missing.png"
    filename_difficulty = "summary_difficulty.png"
    
    path_missing = BASE_DIR / "static" / filename_missing
    path_difficulty = BASE_DIR / "static" / filename_difficulty
    
    generate_summary_graphs(missing_counter, suggestions, path_missing, path_difficulty)

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
        graph_missing_url=url_for('static', filename=filename_missing),
        graph_difficulty_url=url_for('static', filename=filename_difficulty)
    )


@app.route("/favourites")
def favourites():
    recipes_list = load_recipes(RECIPES_FILE)
    favourite_recipe_names = read_favourite_recipe_names(FAVOURITES_FILE)
    favourite_recipes = [
        recipe
        for recipe in add_favourite_status(recipes_list, favourite_recipe_names)
        if recipe_key(recipe.get("name", "")) in favourite_recipe_names
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
        add_favourite_recipe(recipe_name, FAVOURITES_FILE)
        flash(f"{recipe_name} added to favourites.", "success")

    return redirect(request.referrer or url_for("favourites"))


@app.route("/favourites/remove", methods=["POST"])
def remove_from_favourites():
    recipe_name = request.form.get("recipe_name", "")

    if not recipe_key(recipe_name):
        flash("Recipe could not be removed from favourites.", "error")
    else:
        remove_favourite_recipe(recipe_name, FAVOURITES_FILE)
        flash(f"{recipe_name} removed from favourites.", "success")

    return redirect(request.referrer or url_for("favourites"))


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
