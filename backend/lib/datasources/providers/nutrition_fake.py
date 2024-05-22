from lib.service.interfaces import nutrition 

class NutritionProviderImpl(nutrition.NutritionProvider):
    def __init__(self) -> None:
        pass

    def get_nutrition(self, meal_description: str) -> nutrition.NutritionInfo:
        return nutrition.NutritionInfo(calories=500.0)
