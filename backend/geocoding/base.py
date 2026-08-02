"""
base.py

"""

from abc import ABC, abstractmethod

class Geocoder(ABC):
    """
    Template class for geocoding places.
    """

    @abstractmethod
    def geocode(self, address: str):
        pass