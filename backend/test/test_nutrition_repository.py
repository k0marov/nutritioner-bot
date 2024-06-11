"""File for testing the nutrition_repository."""

import unittest
from datetime import datetime, timedelta


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.database.models import Base, Meal
from lib.database.session import NutritionRepository


DATABASE_URL = "sqlite:///:memory:"


def init_test_db():
    """Initialize the test database.

    Returns:
        sessionmaker: Session for database.
    """
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestNutritionRepository(unittest.TestCase):
    """Tests for NutritionRepository."""

    @classmethod
    def setUpClass(cls):
        """Set up the test database connection."""
        cls.SessionLocal = init_test_db()

    def setUp(self):
        """Set up a test environment before running tests."""
        self.session = self.SessionLocal()
        self.repo = NutritionRepository(self.SessionLocal)

    def tearDown(self):
        """Tear down the test environment after running tests."""
        self.session.rollback()
        self.session.query(Meal).delete()
        self.session.commit()
        self.session.close()

    def test_insert_meal(self):
        """Test inserting a meal into the database."""
        user_id = 'test_user'
        description = 'test meal'
        calories = 100.0
        created_date = datetime.now()

        output = self.repo.insert_meal(user_id, description, calories, created_date)

        self.assertEqual(output['status'], 'success')

        meal = self.session.query(Meal).filter_by(user_id=user_id).first()
        self.assertIsNotNone(meal)
        self.assertEqual(meal.description, description)
        self.assertEqual(meal.calories, calories)
        self.assertEqual(meal.created_date, created_date)

    def test_get_meals_for_last_week(self):
        """Test retrieving meals for the last week."""
        user_id = 'test_user'
        now = datetime.now()
        meals = [
            Meal(
                user_id=user_id, description='meal1',
                calories=100.0, created_date=now,
            ),
            Meal(
                user_id=user_id, description='meal2',
                calories=200.0, created_date=now - timedelta(days=1),
            ),
            Meal(
                user_id=user_id, description='meal3',
                calories=300.0, created_date=now - timedelta(days=8),
            ),
        ]

        self.session.add_all(meals)
        self.session.commit()

        output = self.repo.get_meals_for_last_week(user_id)

        self.assertEqual(len(output), 2)
        self.assertTrue(all(meal.created_date >= now - timedelta(days=7) for meal in output))
        self.assertTrue(all(meal.user_id == user_id for meal in output))


if __name__ == '__main__':
    unittest.main()
