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
  - .json for recipe
  - .txt for saved user ingredients
  - .txt for exports


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










