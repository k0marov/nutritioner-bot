"""HTTP nutrition server."""
import datetime
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from lib import config
from lib.database.session import BaseNutritionRepository
from lib.service.interfaces import nutrition


def nutrition_handler_factory(
    nutrition_provider: nutrition.NutritionProvider,
    nutrition_repository: BaseNutritionRepository,
):
    """Create class NutritionerHandler.

    Args:
        nutrition_provider (nutrition.NutritionProvider): class that provides interface.
        nutrition_repository (BaseNutritionRepository): class that provides interface.

    Returns:
        NutritionerHandler: class for HTTP server.
    """
    class NutritionerHandler(SimpleHTTPRequestHandler):
        def do_POST(self):
            if self.path != '/api/v1/meals':
                self.send_response(config.NOT_FOUND)
                self.end_headers()
                return

            content_length = int(self.headers[config.HEADER_LENGTH])
            body = self.rfile.read(content_length)
            meal_info = json.loads(body)

            if 'user_id' not in meal_info or 'description' not in meal_info:
                self.send_response(config.BAD_REQUEST)
                self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
                self.end_headers()
                response = {
                    'error': 'Invalid request, missing user_id or description',
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            user_id = meal_info['user_id']
            description = meal_info['description']
            if 'created_date' in meal_info:
                created_date = meal_info['created_date']
            else:
                created_date = datetime.datetime.now()

            try:
                nutrition_info = nutrition_provider.get_nutrition(meal_description=description)
            except Exception as err:
                self.send_response(config.BAD_REQUEST)
                self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
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
                created_date=created_date,
            )

            if response['status'] == 'error':
                self.send_response(config.INTERNAL_SERVER_ERROR)
                self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            self.send_response(config.OK)
            self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
            self.end_headers()
            response = {"calories": nutrition_info.calories}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        def do_GET(self):
            if self.path.startswith('/api/v1/stats'):
                query_components = parse_qs(urlparse(self.path).query)
                user_id = query_components.get('user_id', [None])[0]

                if not user_id:
                    self.send_response(config.BAD_REQUEST)
                    self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
                    self.end_headers()
                    response = {'error': 'Missing user_id parameter'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                meals = nutrition_repository.get_meals_for_last_week(user_id)

                if isinstance(meals, dict) and meals.get('status') == 'error':
                    self.send_response(config.INTERNAL_SERVER_ERROR)
                    self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
                    self.end_headers()
                    self.wfile.write(json.dumps(meals).encode('utf-8'))
                    return

                if not meals:
                    self.send_response(config.NOT_FOUND)
                    self.end_headers()
                    return

                past_data = [
                    nutrition.NutritionInfo(
                        calories=sum(
                            [
                                meal.calories for meal in meals if meal.created_date.date()
                                == datetime.datetime.now().date() - datetime.timedelta(days=day)
                            ],
                        ),
                    ) for day in range(7)
                ]
                past_data = [inform if inform.calories else None for inform in past_data]

                try:
                    recommendations = nutrition_provider.get_recommendations(past_data)
                except Exception as err:
                    self.send_response(config.INTERNAL_SERVER_ERROR)
                    self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
                    self.end_headers()
                    response = {'error': 'Error fetching recommendations', 'details': str(err)}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                self.send_response(config.OK)
                self.send_header(config.HEADER_TYPE, config.JSON_TYPE)
                self.end_headers()
                response = {"recommendations": recommendations}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return

            self.send_response(config.NOT_FOUND)
            self.end_headers()
            return

    return NutritionerHandler


def run(
    nutrition_repository: BaseNutritionRepository,
    nutrition_provider: nutrition.NutritionProvider,
    server_class=HTTPServer, port=8000,
):
    """Start the server.

    Args:
        nutrition_repository (BaseNutritionRepository): class that provides interface.
        nutrition_provider (nutrition.NutritionProvider): class that provides interface.
        server_class (_type_, optional): defaults to HTTPServer.
        port (int, optional): port for server. Defaults to 8000.
    """
    handler_class = nutrition_handler_factory(nutrition_provider, nutrition_repository)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
