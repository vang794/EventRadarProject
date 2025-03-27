import json
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = 'Exports static landmarks from Geoapify Places API to a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('--location', type=str, default='Milwaukee', help='City to fetch landmarks for')
        parser.add_argument('--radius', type=int, default=5000, help='Radius in meters (max 5000)')
        parser.add_argument('--limit', type=int, default=50, help='Maximum number of landmarks per category')
        parser.add_argument('--key', type=str, required=True, help='Geoapify API key')
        parser.add_argument('--output', type=str, default='landmarks.json', help='Output JSON file')

    def handle(self, *args, **options):
        location = options['location']
        radius = min(options['radius'], 5000)  # API limit is 5000m
        limit = options['limit']
        api_key = options['key']
        output_file = options['output']

        # Get coordinates for the location
        geocode_url = f"https://api.geoapify.com/v1/geocode/search?text={location}&format=json&apiKey={api_key}"
        geocode_response = requests.get(geocode_url)
        
        if geocode_response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed to geocode location: {geocode_response.text}'))
            return
            
        geocode_data = geocode_response.json()
        if not geocode_data.get('results'):
            self.stdout.write(self.style.ERROR(f'No results found for location: {location}'))
            return
            
        lat = geocode_data['results'][0]['lat']
        lon = geocode_data['results'][0]['lon']
        
        categories = [
            # Parking
            'parking.cars',
            
            # Tourism attractions
            'tourism.attraction',
            'tourism.attraction.artwork',
            'tourism.attraction.viewpoint',
            'tourism.attraction.fountain',
            
            # Tourism sights
            'tourism.sights.windmill',
            'tourism.sights.tower',
            'tourism.sights.battlefield',
            'tourism.sights.fort',
            'tourism.sights.castle',
            'tourism.sights.ruines',
            'tourism.sights.archaeological_site',
            
            # Memorials
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
            
            # Entertainment
            'entertainment.theme_park',
            'entertainment.water_park',
            'entertainment.activity_park',
            'entertainment.culture',
            'entertainment.culture.theatre',
            'entertainment.culture.arts_centre',
            'entertainment.culture.gallery',
            'entertainment.zoo',
            'entertainment.aquarium',
            'entertainment.planetarium',
            'entertainment.museum',
            
            # Buildings
            'building.tourism',
            'building.historic',
        ]
        
        landmarks = []
        
        for category in categories:
            self.stdout.write(f'Fetching {category} landmarks...')
            
            places_url = f"https://api.geoapify.com/v2/places"
            params = {
                'categories': category,
                'filter': f'circle:{lon},{lat},{radius}',
                'limit': limit,
                'apiKey': api_key
            }
            
            response = requests.get(places_url, params=params)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'API request failed: {response.text}'))
                continue
                
            data = response.json()
            
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                if not geometry or not props.get('name'):
                    continue
                    
                category_mapping = {
                    'parking.cars': 'Parking',
                    
                    # Tourism categories
                    'tourism.attraction': 'Attraction',
                    'tourism.attraction.artwork': 'Artwork',
                    'tourism.attraction.viewpoint': 'Viewpoint',
                    'tourism.attraction.fountain': 'Fountain',
                    'tourism.sights.windmill': 'Windmill',
                    'tourism.sights.tower': 'Tower',
                    'tourism.sights.battlefield': 'Battlefield',
                    'tourism.sights.fort': 'Fort',
                    'tourism.sights.castle': 'Castle',
                    'tourism.sights.ruines': 'Ruins',
                    'tourism.sights.archaeological_site': 'Archaeological Site',
                    
                    # Memorial categories
                    'tourism.sights.memorial': 'Memorial',
                    'tourism.sights.memorial.aircraft': 'Aircraft Memorial',
                    'tourism.sights.memorial.locomotive': 'Locomotive Memorial',
                    'tourism.sights.memorial.railway_car': 'Railway Car Memorial',
                    'tourism.sights.memorial.ship': 'Ship Memorial',
                    'tourism.sights.memorial.tank': 'Tank Memorial',
                    'tourism.sights.memorial.tomb': 'Tomb',
                    'tourism.sights.memorial.monument': 'Monument',
                    'tourism.sights.memorial.wayside_cross': 'Wayside Cross',
                    'tourism.sights.memorial.boundary_stone': 'Boundary Stone',
                    'tourism.sights.memorial.pillory': 'Pillory',
                    'tourism.sights.memorial.milestone': 'Milestone',
                    
                    # Entertainment categories
                    'entertainment.theme_park': 'Theme Park',
                    'entertainment.water_park': 'Water Park',
                    'entertainment.activity_park': 'Activity Park',
                    'entertainment.culture': 'Cultural Venue',
                    'entertainment.culture.theatre': 'Theatre',
                    'entertainment.culture.arts_centre': 'Arts Centre',
                    'entertainment.culture.gallery': 'Gallery',
                    'entertainment.zoo': 'Zoo',
                    'entertainment.aquarium': 'Aquarium',
                    'entertainment.planetarium': 'Planetarium',
                    'entertainment.museum': 'Museum',
                    
                    # Building categories
                    'building.tourism': 'Tourist Building',
                    'building.historic': 'Historic Building',
                }
                
                cat_parts = category.split('.')
                specific_cat = category
                general_cat = '.'.join(cat_parts[:2]) 
                
                category_label = (
                    category_mapping.get(specific_cat) or 
                    category_mapping.get(general_cat) or 
                    'Landmark'
                )
                
                landmark = {
                    'title': props.get('name', 'Unnamed Landmark'),
                    'description': self._build_description(props),
                    'location_name': props.get('formatted', ''),
                    'latitude': geometry['coordinates'][1],
                    'longitude': geometry['coordinates'][0],
                    'category': category_label
                }
                
                landmarks.append(landmark)
                
            self.stdout.write(self.style.SUCCESS(f'Processed {category} landmarks'))
            
        with open(output_file, 'w') as f:
            json.dump(landmarks, f, indent=2)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully exported {len(landmarks)} landmarks to {output_file}'))
    
    def _build_description(self, props):
        """Build a descriptive text from the place properties"""
        description = []
        
        if props.get('categories'):
            description.append(f"Type: {', '.join(props['categories'])}")
            
        if props.get('address_line1'):
            description.append(f"Address: {props['address_line1']}")
            
        if props.get('address_line2'):
            description.append(props['address_line2'])
            
        if props.get('opening_hours'):
            description.append(f"Hours: {props['opening_hours']}")
            
        if props.get('phone'):
            description.append(f"Phone: {props['phone']}")
            
        if props.get('website'):
            description.append(f"Website: {props['website']}")
            
        return "\n".join(description) 