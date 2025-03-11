import requests
from django.conf import settings


class GeocodingService:
    def __init__(self, service_name=None):
        self.service_name = service_name or settings.GEOCODING_SERVICE
        self.user_agent = settings.NOMINATIM_USER_AGENT
        self.base_url = settings.NOMINATIM_BASE_URL

    def _get_coordinates_nominatim(self, location_string):
        try:
            if location_string.isdigit() and len(location_string) == 5:
                url = f"{self.base_url}?postalcode={location_string}&countrycodes=US&format=json"
            else:
                url = f"{self.base_url}?q={location_string}&format=json"

            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                return None
        except (requests.exceptions.RequestException, KeyError, IndexError, ValueError) as e:
            print(f"Geocoding error: {e}") 
            return None

    def get_coordinates(self, location_string):
        if self.service_name == 'nominatim':
            return self._get_coordinates_nominatim(location_string)
        else:
            raise NotImplementedError(f"Geocoding service '{self.service_name}' not supported.") 