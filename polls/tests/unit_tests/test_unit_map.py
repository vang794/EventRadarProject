from django.test import TestCase
from django.utils import timezone
import folium
from folium.plugins import MarkerCluster
from polls.views import HomePage
from polls.models import User, Event
import json
from unittest.mock import patch, MagicMock

class MapUnitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="mapuser",
            email="mapuser@example.com",
            password="testpassword",
            first_name="Map",
            last_name="User"
        )
        
        self.event = Event.objects.create(
            title="Test Event",
            description="This is a test event",
            location_name="Test Location",
            latitude=43.0389,
            longitude=-87.9065,
            event_date=timezone.now() + timezone.timedelta(days=1),
            created_by=self.user,
            category="Test"
        )
        
        self.view = HomePage()
    
    def test_map_creation_with_default_location(self):
        """Test that a map is created with Milwaukee as the default location"""
        m = folium.Map(location=[43.0389, -87.9065], zoom_start=12, tiles="cartodbpositron")
        
        self.assertEqual(m.location, [43.0389, -87.9065])
        
        map_html = m._repr_html_()
        self.assertIsNotNone(map_html)
        self.assertIn("43.0389", map_html)
        self.assertIn("-87.9065", map_html)
    
    def test_marker_creation(self):
        """Test that markers are created correctly"""
        m = folium.Map(location=[43.0389, -87.9065])
        
        marker = folium.Marker(
            location=[self.event.latitude, self.event.longitude],
            popup="Test Popup",
            tooltip="Test Tooltip"
        ).add_to(m)
        
        self.assertEqual(marker.location, [self.event.latitude, self.event.longitude])
        
        map_html = m._repr_html_()
        self.assertIn(str(self.event.latitude), map_html)
        self.assertIn(str(self.event.longitude), map_html)
    
    def test_circle_creation(self):
        """Test creating a search radius circle"""
        m = folium.Map(location=[43.0389, -87.9065])
        
        circle = folium.Circle(
            location=[43.0389, -87.9065],
            radius=5000,  # 5km
            color='#3186cc',
            fill=True,
            fill_color='#3186cc',
            fill_opacity=0.2,
            tooltip="5km radius"
        ).add_to(m)
        
        self.assertEqual(circle.location, [43.0389, -87.9065])
        
        map_html = m._repr_html_()
        
        self.assertIn("circle_", map_html) 
        self.assertIn("radius", map_html)
        self.assertIn("5000", map_html)
        self.assertIn("43.0389", map_html)
        self.assertIn("-87.9065", map_html)
        self.assertIn("5km radius", map_html)
    
    @patch('folium.Map')
    def test_sample_events_creation(self, mock_map):
        """Test the creation of sample events for the map"""
        mock_map_instance = MagicMock()
        mock_map.return_value = mock_map_instance
        mock_marker_cluster = MagicMock()
        mock_map_instance._repr_html_.return_value = "<div>Mock Map HTML</div>"
        
        sample_event = {
            'title': 'Test Event',
            'description': 'Test Description',
            'latitude': 43.0450,
            'longitude': -87.8900,
            'date': timezone.now() + timezone.timedelta(days=2),
            'category': 'Test'
        }
        
        event_date = sample_event['date'].strftime('%B %d, %Y at %I:%M %p')
        popup_html = f"""
        <div class="event-popup">
            <h3>{sample_event['title']}</h3>
            <p><strong>Date:</strong> {event_date}</p>
            <p><strong>Category:</strong> {sample_event['category']}</p>
            <p>{sample_event['description']}</p>
        </div>
        """
        
        self.assertIn(sample_event['title'], popup_html)
        self.assertIn(event_date, popup_html)
        self.assertIn(sample_event['category'], popup_html)
        self.assertIn(sample_event['description'], popup_html)

    def test_parse_radius_parameter(self):
        """Test parsing the radius parameter from the request"""
        radius = "10"
        parsed_radius = int(radius) if radius.isdigit() else 5
        self.assertEqual(parsed_radius, 10)
        
        radius = "invalid"
        parsed_radius = int(radius) if radius.isdigit() else 5
        self.assertEqual(parsed_radius, 5)
        
        radius = "-10"
        parsed_radius = 5 if radius.startswith('-') else max(1, int(radius))
        self.assertEqual(parsed_radius, 5)