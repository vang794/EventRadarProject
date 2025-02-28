from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from polls.models import User, Event
from bs4 import BeautifulSoup

class MapAcceptanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create(
            username="mapuser",
            email="mapuser@example.com",
            password="testpassword",
            first_name="Map",
            last_name="User"
        )
        
        session = self.client.session
        session['email'] = self.user.email
        session.save()
        
        self.event = Event.objects.create(
            title="Test Real Event",
            description="This is a test event in the database",
            location_name="Milwaukee Downtown",
            latitude=43.0389,
            longitude=-87.9065,
            event_date=timezone.now() + timezone.timedelta(days=1),
            created_by=self.user,
            category="Test"
        )
    
    def test_homepage_displays_map(self):
        """Test that the homepage displays a map"""
        response = self.client.get(reverse('homepage'))
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        self.assertIn('map-container', content)
        self.assertIn('folium-map', content, "Folium map div should be in the response")
        
        self.assertIn('leaflet.js', content, "Leaflet JS should be included")
    
    def test_homepage_shows_sample_events(self):
        """Test that the homepage shows sample events"""
        response = self.client.get(reverse('homepage'))
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        event_cards = soup.select('.event-card')
        
        self.assertTrue(len(event_cards) > 0, "Should display event cards")
        
        sample_event_titles = ['Music in the Park', 'Food Festival', 'Art Exhibition', 'Tech Meetup']
        found_titles = []
        
        for card in event_cards:
            title = card.select_one('.event-header h3')
            if title:
                found_titles.append(title.text.strip())
        
        self.assertTrue(any(title in found_titles for title in sample_event_titles), 
                        f"At least one sample event should be displayed. Found: {found_titles}")
    
    def test_search_parameters_form_displayed(self):
        """Test that the search parameters form is displayed"""
        response = self.client.get(reverse('homepage'))
        
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        search_form = soup.select('form[action*="homepage"]')
        self.assertTrue(len(search_form) > 0, "Search form should be displayed")
        
        location_input = soup.select('input[name="location"]')
        self.assertTrue(len(location_input) > 0, "Location input should be displayed")
        self.assertEqual(location_input[0].get('value'), 'Milwaukee', "Default location should be Milwaukee")
        
        radius_input = soup.select('input[name="radius"]')
        self.assertTrue(len(radius_input) > 0, "Radius input should be displayed")
        self.assertEqual(radius_input[0].get('value'), '5', "Default radius should be 5")
    
    def test_search_form_submission(self):
        """Test submitting the search form"""
        response = self.client.post(reverse('homepage'), {
            'location': 'Chicago',
            'radius': '10'
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        self.assertIn('map-container', content)
        self.assertIn('folium-map', content)
    
    def test_map_and_event_list_integration(self):
        """Test that the map and event list show the same events"""
        response = self.client.get(reverse('homepage'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        event_cards = soup.select('.event-card')
        event_titles_in_list = []
        
        for card in event_cards:
            title = card.select_one('.event-header h3')
            if title:
                event_titles_in_list.append(title.text.strip())
        
        
        map_html = soup.select_one('.map-container').decode_contents()
        
        for title in event_titles_in_list:
            self.assertIn(title, map_html, f"Event '{title}' should appear in map HTML") 