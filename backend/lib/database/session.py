"""File with class NutritionRepository for interactions with the database."""


import abc

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
