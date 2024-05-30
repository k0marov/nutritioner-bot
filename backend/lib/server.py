"""HTTP nutrition server."""
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from lib.database.session import BaseNutritionRepository, NutritionRepository, SessionLocal
from lib.config import (BAD_REQUEST, HEADER_LENGTH, HEADER_TYPE,
                        INTERNAL_SERVER_ERROR, JSON_TYPE, NOT_FOUND, OK)
from lib.service.interfaces.nutrition import NutritionProvider
from lib.database.models import Meal
from lib.service.interfaces import nutrition


def nutrition_handler_factory(nutrition_provider: NutritionProvider, nutrition_repository: BaseNutritionRepository):
    """Create class NutritionerHandler.

    Args:
        nutrition_provider (NutritionProvider): class that provides interface.
        nutrition_repository (BaseNutritionRepository): class that provides interface.

    Returns:
        NutritionerHandler: class for HTTP server.
    """
    class NutritionerHandler(SimpleHTTPRequestHandler):
        def do_POST(self):
            if self.path != '/api/v1/meals':
                self.send_response(NOT_FOUND)
                self.end_headers()
                return

            content_length = int(self.headers[HEADER_LENGTH])
            body = self.rfile.read(content_length)
            info = json.loads(body)

            if 'user_id' not in info or 'description' not in info:
                self.send_response(BAD_REQUEST)
                self.send_header(HEADER_TYPE, JSON_TYPE)
                self.end_headers()
                response = {
                    'error': 'Invalid request, missing user_id or description',
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            user_id = info['user_id']
            description = info['description']

            try:
                nutrition_info = nutrition_provider.get_nutrition(
                    meal_description=description)
            except Exception as err:
                self.send_response(BAD_REQUEST)
                self.send_header(HEADER_TYPE, JSON_TYPE)
                self.end_headers()
                response = {
                    'error': 'Server did not recognize the request.',
                    'details': str(err),
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            response = nutrition_repository.insert_meal(
                user_id=user_id,
                description=description,
                calories=nutrition_info.calories,
            )

            if response['status'] == 'error':
                self.send_response(INTERNAL_SERVER_ERROR)
                self.send_header(HEADER_TYPE, JSON_TYPE)
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            self.send_response(OK)
            self.send_header(HEADER_TYPE, JSON_TYPE)
            self.end_headers()
            response = {"calories": nutrition_info.calories}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        def do_GET(self):
            if self.path.startswith('/api/v1/stats'):
                query_components = parse_qs(urlparse(self.path).query)
                user_id = query_components.get('user_id', [None])[0]

                if not user_id:
                    self.send_response(BAD_REQUEST)
                    self.send_header(HEADER_TYPE, JSON_TYPE)
                    self.end_headers()
                    response = {'error': 'Missing user_id parameter'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                meals = nutrition_repository.get_meals_for_last_week(user_id)

                if isinstance(meals, dict) and meals.get('status') == 'error':
                    self.send_response(INTERNAL_SERVER_ERROR)
                    self.send_header(HEADER_TYPE, JSON_TYPE)
                    self.end_headers()
                    self.wfile.write(json.dumps(meals).encode('utf-8'))
                    return

                past_data = [nutrition.NutritionInfo(calories=meal.calories) for meal in meals]

                try:
                    recommendations = nutrition_provider.get_recommendations(past_data)
                except Exception as err:
                    self.send_response(INTERNAL_SERVER_ERROR)
                    self.send_header(HEADER_TYPE, JSON_TYPE)
                    self.end_headers()
                    response = {'error': 'Error fetching recommendations', 'details': str(err)}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                self.send_response(OK)
                self.send_header(HEADER_TYPE, JSON_TYPE)
                self.end_headers()
                response = {"recommendations": recommendations}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            self.send_response(NOT_FOUND)
            self.end_headers()
            return

    return NutritionerHandler


def run(
    nutrition_repository: BaseNutritionRepository,
    nutrition_provider: NutritionProvider,
    server_class=HTTPServer, port=8000,
):
    """Start the server.

    Args:
        nutrition_provider (NutritionProvider): class that provides interface.
        server_class (_type_, optional): defaults to HTTPServer.
        port (int, optional): port for server. Defaults to 8000.
    """
    handler_class = nutrition_handler_factory(nutrition_provider, nutrition_repository)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting http server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
