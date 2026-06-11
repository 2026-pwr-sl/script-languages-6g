import json
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter


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


def add_user_ingredient(ingredient, filepath):
    current_ingredients = read_user_ingredients(filepath)
    
    item = clean_ingredient(ingredient)

    if item and item not in current_ingredients:
        current_ingredients.append(item)
        
        save_user_ingredients(current_ingredients, filepath)


def recipe_key(recipe_name):
    return clean_ingredient(recipe_name)


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


def read_user_ingredients(filepath):
    path = Path(filepath)

    if not path.exists():
        return []

    return [
        clean_ingredient(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if clean_ingredient(line)
    ]


def read_shopping_list(filepath):
    path = Path(filepath)

    if not path.exists():
        return []

    return [
        clean_ingredient(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if clean_ingredient(line)
    ]


def save_shopping_list(items, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    unique_items = sorted(set(clean_ingredient(item) for item in items if clean_ingredient(item)))
    path.write_text("\n".join(unique_items), encoding="utf-8")


def read_favourite_recipe_names(filepath):
    path = Path(filepath)

    if not path.exists():
        return []

    return [
        recipe_key(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if recipe_key(line)
    ]


def save_favourite_recipe_names(recipe_names, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    unique_recipe_names = []
    seen_names = set()

    for recipe_name in recipe_names:
        name = recipe_key(recipe_name)

        if name and name not in seen_names:
            unique_recipe_names.append(name)
            seen_names.add(name)

    path.write_text("\n".join(unique_recipe_names), encoding="utf-8")


def add_favourite_recipe(recipe_name, filepath):
    favourite_names = read_favourite_recipe_names(filepath)
    favourite_names.append(recipe_name)
    save_favourite_recipe_names(favourite_names, filepath)


def remove_favourite_recipe(recipe_name, filepath):
    name_to_remove = recipe_key(recipe_name)
    favourite_names = [
        name
        for name in read_favourite_recipe_names(filepath)
        if name != name_to_remove
    ]

    save_favourite_recipe_names(favourite_names, filepath)


def add_missing_to_shopping_list(missing_items, filepath):
    current_items = read_shopping_list(filepath)
    new_items = [
        clean_ingredient(item)
        for item in missing_items
        if clean_ingredient(item)
    ]

    save_shopping_list(current_items + new_items, filepath)


def remove_from_shopping_list(item, filepath):
    item_to_remove = clean_ingredient(item)
    current_items = read_shopping_list(filepath)

    updated_items = [
        ingredient
        for ingredient in current_items
        if ingredient != item_to_remove
    ]

    save_shopping_list(updated_items, filepath)


def build_shopping_report(shopping_items, matched_recipes):
    if not shopping_items:
        return "Shopping list is empty."

    return "\n".join(f"- {item}" for item in shopping_items)


def generate_summary_graphs(missing_counter, suggestions, path_missing, path_difficulty):
    fig1 = plt.figure(figsize=(6, 5))
    fig1.patch.set_facecolor('#f4f7fb')
    ax1 = fig1.add_subplot(111)

    if missing_counter:
        top_missing = missing_counter.most_common(5)
        names = [item[0].capitalize() for item in top_missing]
        counts = [item[1] for item in top_missing]
        
        ax1.bar(names, counts, color='#0C9961', edgecolor='#0a8253', alpha=0.8)
        ax1.set_title("Most Needed Ingredients", fontsize=12, fontweight='bold', color='#1f4f46')
        ax1.set_ylabel("Recipe Appearances")
        ax1.grid(axis='y', linestyle='--', alpha=0.5)
    else:
        ax1.text(0.5, 0.5, "No missing data", ha='center', va='center')

    plt.tight_layout()
    fig1.savefig(path_missing, dpi=200, facecolor=fig1.get_facecolor(), edgecolor='none')
    plt.close(fig1)

    fig2 = plt.figure(figsize=(6, 5))
    fig2.patch.set_facecolor('#f4f7fb')
    ax2 = fig2.add_subplot(111)

    if suggestions:
        difficulties = [s.get('difficulty', 'Unknown') for s in suggestions]
        diff_counts = Counter(difficulties)
        
        colors = ['#0C9961', '#f59e0b', '#ef4444', '#94a3b8'] 
        ax2.pie(diff_counts.values(), labels=diff_counts.keys(), autopct='%1.1f%%', colors=colors)
        ax2.set_title("Recipe Difficulty Levels", fontsize=12, fontweight='bold', color='#1f4f46')
    else:
        ax2.text(0.5, 0.5, "No difficulty data", ha='center', va='center')

    plt.tight_layout()
    fig2.savefig(path_difficulty, dpi=200, facecolor=fig2.get_facecolor(), edgecolor='none')
    plt.close(fig2)