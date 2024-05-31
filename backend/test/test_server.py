import pytest 
import datetime
import threading
from lib.server import nutrition_handler_factory
from lib.database.models import Meal
from unittest import mock
from lib.service.interfaces.nutrition import NutritionInfo 
import http
import unittest
import requests

class TestHTTPServer(unittest.TestCase):
    def setUp(self):
        self.repo_mock = mock.Mock()
        self.provider_mock = mock.Mock()

        handler = nutrition_handler_factory(self.provider_mock, self.repo_mock)
        self.server = http.server.HTTPServer(('localhost', 0), handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
    
    def _get_url(self) -> str: 
        return f'http://localhost:{self.port}'

    def test_POST(self): 
        nutrition_info = NutritionInfo(calories=42)
        self.provider_mock.get_nutrition = mock.MagicMock(return_value=nutrition_info)
        self.repo_mock.insert_meal = mock.MagicMock(return_value={'status': 'ok'})
        test_description = 'test meal description'
        user_id = '42'
        response = requests.post(self._get_url()+'/api/v1/meals', json={
            'user_id': user_id, 
            'description': test_description
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['calories'], nutrition_info.calories)

        self.provider_mock.get_nutrition.assert_called_once_with(meal_description=test_description)
        repo_call = self.repo_mock.insert_meal.call_args.kwargs
        self.assertEqual(repo_call['user_id'], user_id)
        self.assertEqual(repo_call['description'], test_description)
        self.assertEqual(repo_call['calories'], nutrition_info.calories)
        self.assertEqual(repo_call['created_date'].date(), datetime.datetime.now().date())

    def test_POST(self): 
        user_id = '42'
        now = datetime.datetime.now()
        saved_meals = [
            Meal(calories=100, created_date=now), 
            Meal(calories=200, created_date=now-datetime.timedelta(milliseconds=5)),
            Meal(calories=400, created_date=now-datetime.timedelta(days=2)),
            Meal(calories=1000, created_date=now-datetime.timedelta(days=4)),
        ]
        expected_flattened = [NutritionInfo(calories=300), None, NutritionInfo(calories=400), None, NutritionInfo(calories=1000), None, None]
        self.repo_mock.get_meals_for_last_week = mock.MagicMock(return_value=saved_meals)

        test_recommendations = 'test recommendations'
        self.provider_mock.get_recommendations = mock.MagicMock(return_value=test_recommendations)

        response = requests.get(self._get_url()+'/api/v1/stats', params={
            'user_id': user_id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['recommendations'], test_recommendations)

        self.repo_mock.get_meals_for_last_week.assert_called_once_with(user_id)
        self.provider_mock.get_recommendations.assert_called_once_with(expected_flattened)