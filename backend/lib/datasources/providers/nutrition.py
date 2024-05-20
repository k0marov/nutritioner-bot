import json 
import requests 
from lib.service.interfaces import nutrition 

class NutritionProviderImpl(nutrition.NutritionProvider):
    def __init__(self, ollama_url: str, ollama_model: str) -> None: 
        self.ollama_url = ollama_url 
        self.ollama_model = ollama_model

    def get_nutrition(self, meal_description: str) -> nutrition.NutritionInfo:
        prompt = f'Сколько килокалорий в: "{meal_description}"? Отвечай только числом, без букв, среднее значение'
        body = json.dumps({"model": self.ollama_model, "prompt": prompt, "stream": False})
        r = requests.post(f'{self.ollama_url}/api/generate', data=body)
        resp = r.json() 
        print('got response from ollama', resp)
        return nutrition.NutritionInfo(calories=float(resp["response"]))