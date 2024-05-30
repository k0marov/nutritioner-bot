from dataclasses import dataclass 
from lib.dto import NutritionInfo
import requests
import json 

class Backend:
    def __init__(self, base_url: str) -> None: 
        self._base_url = base_url 
    def get_nutrition_info(self, user_id: str, description: str) -> NutritionInfo:
        body = json.dumps({"description": description, "user_id": user_id})
        r = requests.post(f'{self._base_url}/api/v1/meals', data=body)
        if r.status_code != 200: 
            raise Exception(f'got non-200 status code from backend: {r.status_code}')
        resp = r.json() 
        return NutritionInfo(calories=resp["calories"]) 
    def get_recommendations(self, user_id: str) -> str: 
        r = requests.get(f'{self._base_url}/api/v1/stats', params={'user_id': user_id})
        if r.status_code != 200: 
            raise Exception(f'got non-200 status code from backend: {r.status_code}')
        resp = r.json() 
        return resp['recommendations']
