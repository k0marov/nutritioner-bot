import json
import pytest
from http.server import HTTPServer
from io import BytesIO
from unittest.mock import MagicMock

from server import nutrition_handler_factory
from datasources.providers.nutrition_fake import FakeNutritionProvider
from database.session import BaseNutritionRepository


@pytest.fixture
def fake_nutrition_provider():
    return FakeNutritionProvider()


@pytest.fixture
def mock_nutrition_repository(mocker):
    repository = mocker.MagicMock(spec=BaseNutritionRepository)
    repository.insert_meal.return_value = {'status': 'success'}
    return repository


@pytest.fixture
def handler_class(fake_nutrition_provider, mock_nutrition_repository):
    return nutrition_handler_factory(fake_nutrition_provider, mock_nutrition_repository)


def test_post_request(handler_class, mock_nutrition_repository):
    class MockRequest:
        def __init__(self, method, path, headers, body):
            self.method = method
            self.path = path
            self.headers = headers
            self.rfile = BytesIO(body.encode('utf-8'))
            self.wfile = BytesIO()

        def send_response(self, code):
            self.response_code = code

        def send_header(self, header, value):
            pass

        def end_headers(self):
            pass

        def handle(self):
            handler = handler_class(self, ('127.0.0.1', 12345), None)
            handler.handle_one_request()
            self.wfile.seek(0)
            return self.wfile.read()

    user_id = '123'
    description = 'test meal'
    body = json.dumps({'user_id': user_id, 'description': description})

    headers = {
        'Content-Length': str(len(body)),
        'Content-Type': 'application/json'
    }

    mock_request = MockRequest('POST', '/api/v1/meals', headers, body)
    response = mock_request.handle()

    assert mock_request.response_code == 200
    assert json.loads(response) == {'calories': 500.0}

    mock_nutrition_repository.insert_meal.assert_called_once_with(
        user_id=user_id, description=description, calories=500.0)
