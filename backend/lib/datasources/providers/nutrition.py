import json 
import requests 
from lib.service.interfaces import nutrition 

GET_CALORIES_PROMPT = """
You are a smart diet app. 
User gives you a description of his meal and you give him the amount of kilocalories, proteins, carbohydrates and fats that this meal had. Use your knowledge about nutrition in food. 
Return ONLY JSON with this format: \{"kilocalories": int, "proteins": int, "carbs": int, "fats": int\}. You can give a reasonable average estimate. If there is some real error (like if provided meal is not food), just place 0 for calories. "calories" should only be an integer number. not a string
Input: "[[INPUT]]"
"""

GET_RECOMMENDATIONS_PROMPT = """
You are a dietologist.
Provide recommendations for a client who entered some data into a nutrition app.
This client is an adult who has normal weight. He does not have a goal of losing weight, he just wants to maintain it. If he consumes less calories than needed for normal life, tell him about it. If he consumes more, also tell him. Give not only general advice, but also advice for specific days, if they differ from others very much.
Answer no more than 150 words, no preface, no general words, more specific recommendations.

Here is a list of PAST kilocalorie intake for days from today to N days ago. Give general analytics on these past days, and some recommendations for the future. Answer only in Russian.
Input: [[INPUT]]
"""

class LLMException(Exception):
    pass

class NutritionProviderImpl(nutrition.NutritionProvider):
    def __init__(self, ollama_url: str, ollama_model: str) -> None: 
        self.ollama_url = ollama_url 
        self.ollama_model = ollama_model

    def get_nutrition(self, meal_description: str) -> nutrition.NutritionInfo:
        prompt = GET_CALORIES_PROMPT.replace("[[INPUT]]", meal_description)
        print(prompt)
        body = json.dumps({"model": self.ollama_model, "prompt": prompt, "stream": False, "format": "json"})
        r = requests.post(f'{self.ollama_url}/api/generate', data=body)
        resp = json.loads(r.json()["response"])
        print(resp)
        calories = resp["kilocalories"]
        if calories == 0: 
            raise LLMException()
        return nutrition.NutritionInfo(calories=float(calories))

    def get_recommendations(self, past_data: list[nutrition.NutritionInfo]) -> str: 
        prompt = GET_RECOMMENDATIONS_PROMPT.replace('[[INPUT]]', str([d.__dict__ for d in past_data]))
        body = json.dumps({"model": self.ollama_model, "prompt": prompt, "stream": False})
        r = requests.post(f'{self.ollama_url}/api/generate', data=body)
        resp = r.json()["response"]
        return resp