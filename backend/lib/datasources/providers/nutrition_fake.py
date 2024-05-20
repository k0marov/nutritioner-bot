from lib.service.interfaces import nutrition 

class NutritionProviderImpl(nutrition.NutritionProvider):
    def get_nutrition(self, meal_description: str) -> nutrition.NutritionInfo:
        return 500