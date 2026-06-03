from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from helpers import load_recipes, match_recipes, parse_ingredients, save_user_ingredients


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECIPES_FILE = DATA_DIR / "recipes.json"
USER_INGREDIENTS_FILE = DATA_DIR / "user_ingredients.txt"

app = Flask(__name__)
app.secret_key = "frinder2137glhfdonthackmeplease"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recipes", methods=["POST"])
def recipes():
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


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=True)