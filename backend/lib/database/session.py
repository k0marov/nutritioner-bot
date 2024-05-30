"""File with class NutritionRepository for interactions with the database."""


import abc


class BaseNutritionRepository(abc.ABC):
    """Class with interface for NutritionRepository."""

    @abc.abstractmethod
    def __init__(self, session) -> None:
        """Create interface for NutritionRepository.

        Args:
            session (_type_): SessionLocal.
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

    def insert_meal(self, meal):
        self.session = self.session()
