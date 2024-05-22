import os
from lib.datasources.providers import nutrition
import server

ollama_url = os.getenv('BASE_OLLAMA_URL')
ollama_model = os.getenv('OLLAMA_MODEL')

nutrition_provider = nutrition.NutritionProviderImpl(ollama_url, ollama_model)

n_info = nutrition_provider.get_nutrition('5 кг мяса')
print('got nutrition info', n_info)

server.run(nutrition_provider)