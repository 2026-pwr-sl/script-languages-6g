from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class RecipeRow(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    instructions = Column(String, nullable=False, default="")
    cooking_time = Column(Integer, nullable=False, default=0)
    difficulty = Column(String, nullable=False, default="Easy")

    recipe_ingredients = relationship(
        "RecipeIngredientRow",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredientRow.position",
    )


class IngredientRow(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    recipe_links = relationship("RecipeIngredientRow", back_populates="ingredient")
    user_links = relationship("UserIngredientRow", back_populates="ingredient")
    shopping_links = relationship("ShoppingListRow", back_populates="ingredient")


class RecipeIngredientRow(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)

    recipe = relationship("RecipeRow", back_populates="recipe_ingredients")
    ingredient = relationship("IngredientRow", back_populates="recipe_links")


class UserIngredientRow(Base):
    __tablename__ = "user_ingredients"

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False, unique=True)

    ingredient = relationship("IngredientRow", back_populates="user_links")


class FavoriteRecipeRow(Base):
    __tablename__ = "favorite_recipes"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, unique=True)

    recipe = relationship("RecipeRow")


class ShoppingListRow(Base):
    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False, unique=True)

    ingredient = relationship("IngredientRow", back_populates="shopping_links")
