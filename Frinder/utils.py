def clean_ingredient(value):
    return str(value).strip().lower()


def parse_ingredients(raw_text):
    if not raw_text:
        return []

    items = raw_text.replace("\n", ",").split(",")
    return [clean_ingredient(item) for item in items if clean_ingredient(item)]


def recipe_key(recipe_name):
    return clean_ingredient(recipe_name)
