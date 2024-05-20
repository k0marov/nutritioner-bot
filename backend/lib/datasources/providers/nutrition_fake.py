from lib.service.interfaces import nutrition 

class NutritionProviderImpl(nutrition.NutritionProvider):
    def get_nutrition(self) -> nutrition.NutritionInfo:
        return 500