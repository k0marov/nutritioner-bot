from dataclasses import dataclass
import abc

@dataclass
class NutritionInfo: 
    calories: float

class NutritionProvider(abc.ABC): 
    @abc.abstractmethod
    def get_nutrition(self, meal_description: str) -> NutritionInfo:
        pass