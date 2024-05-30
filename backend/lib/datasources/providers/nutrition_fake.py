from lib.service.interfaces import nutrition


class FakeNutritionProvider(nutrition.NutritionProvider):
    def __init__(self) -> None:
        pass

    def get_nutrition(self, meal_description: str) -> nutrition.NutritionInfo:
        return nutrition.NutritionInfo(calories=500.0)

    def get_recommendations(self, past_data: list[nutrition.NutritionInfo]) -> str:
        return f'надо меньше есть'
