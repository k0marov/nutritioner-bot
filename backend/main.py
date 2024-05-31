import os
from lib.datasources.providers.nutrition_fake import FakeNutritionProvider
from lib.datasources.providers import nutrition
from lib import server
from lib.database.session import NutritionRepository
from lib.database.main_db import init_db

ollama_url = os.getenv('BASE_OLLAMA_URL')
ollama_model = os.getenv('OLLAMA_MODEL')

nutrition_provider = nutrition.NutritionProviderImpl(ollama_url, ollama_model)
session = init_db()
nutrition_repository = NutritionRepository(session)

server.run(nutrition_repository, nutrition_provider)