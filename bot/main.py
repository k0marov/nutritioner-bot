from lib import bot, backend 
import os 

backend_base_url = os.getenv('BACKEND_BASE_URL')
backend_service = backend.Backend(base_url=backend_base_url)
bot.start_bot(backend_service)