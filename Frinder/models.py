from dataclasses import dataclass, field

from utils import clean_ingredient


@dataclass
class Recipe:
    name: str
    ingredients: list[str]
    instructions: str
    cooking_time: int
    difficulty: str = "Easy"
    available_ingredients: list[str] = field(default_factory=list)
    missing_ingredients: list[str] = field(default_factory=list)
    match_score: float = 0.0
    is_favourite: bool = False

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=str(data.get("name", "Unknown")),
            ingredients=[clean_ingredient(item) for item in data.get("ingredients", [])],
            instructions=str(data.get("instructions", "")),
            cooking_time=int(data.get("cooking_time", 0) or 0),
            difficulty=str(data.get("difficulty", "Easy")),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "ingredients": list(self.ingredients),
            "instructions": self.instructions,
            "cooking_time": self.cooking_time,
            "difficulty": self.difficulty,
            "available_ingredients": list(self.available_ingredients),
            "missing_ingredients": list(self.missing_ingredients),
            "match_score": self.match_score,
            "is_favourite": self.is_favourite,
        }
