"""File with class NutritionRepository for interactions with the database."""


import abc
from datetime import datetime, timedelta

from lib.database.models import Meal


class BaseNutritionRepository(abc.ABC):
    """Class with interface for NutritionRepository."""

    @abc.abstractmethod
    def __init__(self, session) -> None:
        """Create interface for NutritionRepository.

        Args:
            session (_type_): SessionLocal.
        """
        pass

    @abc.abstractmethod
    def insert_meal(self, user_id: str, description: str, calories: float) -> dict:
        """Insert a meal into the database.

        Args:
            user_id (str): ID of the user.
            description (str): description of the meal.
            calories (float): number of calories in the meal.

        Returns:
            dict: response indicating failure.
        """
        pass

    @abc.abstractmethod
    def get_meals_for_last_week(self, user_id: str):
        """Get meals for the last week for a given user.

        Args:
            user_id (str): ID of the user.

        Returns:
            list: list of meals.
        """
        pass


class NutritionRepository(BaseNutritionRepository):
    """Class with session."""

    def __init__(self, session) -> None:
        """Get session for interactions with the database..

        Args:
            session (_type_): SessionLocal.
        """
        self.session = session

    def insert_meal(self, user_id: str, description: str, calories: float):
        session = self.session()
        try:
            meal = Meal(
                user_id=user_id,
                description=description,
                calories=calories,
            )
            session.add(meal)
            session.commit()
        except Exception as err:
            session.rollback()
            return {
                'status': 'error',
                'error': 'Database error',
                'details': str(err)
            }
        finally:
            session.close()

    def get_meals_for_last_week(self, user_id: str):
        session = self.session()
        try:
            one_week_ago = datetime.now() - timedelta(days=7)
            meals = session.query(Meal).filter(
                Meal.user_id == user_id, Meal.created_date == one_week_ago.date()).all()
            return meals
        except Exception as err:
            return {
                'status': 'error',
                'error': 'Database error',
                'details': str(err)
            }
        finally:
            session.close()
