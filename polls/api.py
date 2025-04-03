import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_events_from_api(lat, lon, radius_miles, api_key):
    categories = [
        'parking.cars',
        'tourism.attraction.artwork',
        'tourism.attraction.viewpoint',
        'tourism.attraction.fountain',
        'tourism.sights.windmill',
        'tourism.sights.tower',
        'tourism.sights.battlefield',
        'tourism.sights.fort',
        'tourism.sights.castle',
        'tourism.sights.ruines',
        'tourism.sights.archaeological_site',
        'tourism.sights.memorial',
        'tourism.sights.memorial.aircraft',
        'tourism.sights.memorial.locomotive',
        'tourism.sights.memorial.railway_car',
        'tourism.sights.memorial.ship',
        'tourism.sights.memorial.tank',
        'tourism.sights.memorial.tomb',
        'tourism.sights.memorial.monument',
        'tourism.sights.memorial.wayside_cross',
        'tourism.sights.memorial.boundary_stone',
        'tourism.sights.memorial.pillory',
        'tourism.sights.memorial.milestone',
        'entertainment.theme_park',
        'entertainment.water_park',
        'entertainment.activity_park',
        'entertainment.culture.theatre',
        'entertainment.culture.arts_centre',
        'entertainment.culture.gallery',
        'entertainment.zoo',
        'entertainment.aquarium',
        'entertainment.planetarium',
        'entertainment.museum',
        'building.tourism',
        'building.historic',
    ]

    categories_str = ','.join(categories)
    radius_meters = radius_miles * 1609.34

    api_url = "https://api.geoapify.com/v2/places"
    params = {
        'categories': categories_str,
        'filter': f'circle:{lon},{lat},{radius_meters}',
        'limit': 500,
        'apiKey': api_key
    }

    logger.info(f"Fetching events from Geoapify API. URL: {api_url}, Params: {params}")

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Geoapify API response received. Number of features: {len(data.get('features', []))}")
        return data.get('features', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Geoapify API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing Geoapify API response: {e}")
        return None