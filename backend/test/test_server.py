import pytest 
import datetime
import threading
from lib.server import nutrition_handler_factory
from unittest import mock
from lib.service.interfaces import nutrition 
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
        nutrition_info = nutrition.NutritionInfo(calories=42)
        self.provider_mock.get_nutrition = mock.MagicMock(return_value=nutrition_info)
        self.repo_mock.insert_meal = mock.MagicMock(return_value={'status': 'ok'})
        test_description = 'test meal description'
        user_id = '42'
        response = requests.post(self._get_url()+'/api/v1/meals', json={
            'user_id': user_id, 
            'description': test_description
        })
        self.assertEqual(response.status_code, 200)

        self.provider_mock.get_nutrition.assert_called_once_with(meal_description=test_description)
        repo_call = self.repo_mock.insert_meal.call_args.kwargs
        self.assertEqual(repo_call['user_id'], user_id)
        self.assertEqual(repo_call['description'], test_description)
        self.assertEqual(repo_call['calories'], nutrition_info.calories)
        self.assertEqual(repo_call['created_date'].date(), datetime.datetime.now().date())
