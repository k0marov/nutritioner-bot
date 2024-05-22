from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from config import HEADER_TYPE, JSON_TYPE, HEADER_LENGTH
from lib.datasources.providers import nutrition_fake


class NutritionerHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/v1/meals':
            content_length = int(self.headers[HEADER_LENGTH])
            body = self.rfile.read(content_length)
            info = json.loads(body)

            if 'user_id' not in info or 'description' not in info:
                self.send_response(400)
                self.send_header(HEADER_TYPE, JSON_TYPE)
                self.end_headers()
                response = {'error': 'Invalid request, missing user_id or description'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            user_id = info['user_id']
            description = info['description']

            nutrition_provider = nutrition_fake.NutritionProviderImpl()
                        
            self.send_response(200)
            self.send_header(HEADER_TYPE, JSON_TYPE)
            self.end_headers()
            response = nutrition_provider.get_nutrition(meal_description=description)
            print(response)
            self.wfile.write(json.dumps(response.__dict__).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()




def run(server_class=HTTPServer, handler_class=NutritionerHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting http server on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    run()
