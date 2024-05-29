"""HTTP nutrition server."""
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

from config import (BAD_REQUEST, HEADER_LENGTH, HEADER_TYPE,
                    INTERNAL_SERVER_ERROR, JSON_TYPE, NOT_FOUND, OK)
from lib.datasources.providers import nutrition_fake
from lib.service.interfaces.nutrition import NutritionProvider
from main_db import SessionLocal, init_db
from models import Meal

init_db()


def nutrition_handler_factory(nutrition_provider: NutritionProvider):
    """Create class NutritionerHandler.

    Args:
        nutrition_provider (NutritionProvider): class that provides interface.

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

            nutrition_info = nutrition_provider.get_nutrition(meal_description=description)

            session = SessionLocal()
            try:
                meal = Meal(
                    user_id=user_id,
                    description=description,
                    calories=nutrition_info.calories,
                )
                session.add(meal)
                session.commit()
            except Exception as err:
                session.rollback()
                self.send_response(INTERNAL_SERVER_ERROR)
                self.send_header(HEADER_TYPE, JSON_TYPE)
                self.end_headers()
                response = {'error': 'Database error', 'details': str(err)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            finally:
                session.close()

            self.send_response(OK)
            self.send_header(HEADER_TYPE, JSON_TYPE)
            self.end_headers()
            response = {"calories": nutrition_info.calories}
            self.wfile.write(json.dumps(response).encode('utf-8'))

    return NutritionerHandler


def run(
    nutrition_provider: NutritionProvider, server_class=HTTPServer, port=8000,
):
    """Start the server.

    Args:
        nutrition_provider (NutritionProvider): class that provides interface.
        server_class (_type_, optional): defaults to HTTPServer.
        port (int, optional): port for server. Defaults to 8000.
    """
    handler_class = nutrition_handler_factory(nutrition_provider)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting http server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run(nutrition_fake.FakeNutritionProvider())
