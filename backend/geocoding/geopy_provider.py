"""
geopy_provider.py

"""

#Class dependency
from backend.geocoding.base import Geocoder

#Third-party libraries
from geopy.geocoders import Nominatim

class GeopyGeocoder(Geocoder):

    def __init__(self):
        self.client = Nominatim(user_agent="vibematch")

    def geocode(self, address):

        result = self.client.geocode(address)

        if result is None:
            return None

        return {
            "latitude": result.latitude,
            "longitude": result.longitude
        }