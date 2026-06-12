# Frinder

### Frinder is an application that matches  ingredients user already has and what recipies can they cook based on those.


## Techstack
- ### Backend
  - Python
  - Flask
- ### Frontend
  - Jinja2 templates
  - HTML/CSS
  - Flask flash messages
- ### Data processing
  - pandas
  - matplotlib
- ### Storage formats
  - SQLite for recipes, user ingredients, favourites, and shopping list
  - .json as the recipe import source
  - .txt for ingredients uploads and shopping list exports


## Database

Frinder uses SQLite for persistent storage.

- The database file is stored at `data/frinder.db`
- Recipes, user ingredients, favourites, and shopping list data are saved in SQLite
- `recipes.json` is only used as the manual recipe import source
- If you want to update recipes, edit `data/recipes.json` and run `python import_recipes.py`
- The app does not seed recipes automatically on startup
- The import command replaces all recipe rows and restores favourites by matching recipe names

### Tables

- `recipes`: recipe name, instructions, cooking time, difficulty
- `ingredients`: unique ingredient names
- `recipe_ingredients`: links recipes to ingredients
- `user_ingredients`: ingredients the user has saved
- `favorite_recipes`: recipes marked as favourites
- `shopping_list`: ingredients added to the shopping list

### How recipes are loaded

1. Edit `data/recipes.json`
2. Run `python import_recipes.py`
3. The script replaces the recipe tables in SQLite
4. Ingredients are created automatically from the imported recipes
5. Existing favourites are restored by recipe name


## Pages:

- Home page:
  - Enter or upload ingredients user already has
  - Find recipies button
- Recipes:
    - Recipe suggestions with match %
- All recipies
- Summary
  - Different parameters like:
    - how many available ingredients
    - suggested recipies
    - best match
    - average match
    - most common missing ingredient
    - recommendation (based on %, like <20% => go shopping)
    - common missing ingredients table with count
    - graphs
- Favourites
  - Recipes added to favourites
- Shopping list
  - Generated based on missing ingredients from latest recipe matches
  - Full report (maybe modularized witch checkboxes with parameters)









