import json
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from polls.models import Event, User

class Command(BaseCommand):
    help = 'Imports landmarks from a JSON file into the database, replacing all existing events'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True, help='Input JSON file')
        parser.add_argument('--admin_email', type=str, required=False, help='Admin user email to associate with landmarks (optional)')
        parser.add_argument('--keep-existing', action='store_true', help='Keep existing events instead of replacing them')
        parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')

    def handle(self, *args, **options):
        input_file = options['input']
        admin_email = options.get('admin_email')
        keep_existing = options.get('keep_existing', False)
        force = options.get('force', False)

        if admin_email:
            try:
                admin_user = User.objects.get(email=admin_email)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Admin user with email {admin_email} not found, creating system user instead'))
                admin_user = self._create_system_user()
        else:
            try:
                admin_user = User.objects.get(email='system@eventradar.local')
            except User.DoesNotExist:
                admin_user = self._create_system_user()

        try:
            with open(input_file, 'r') as f:
                landmarks = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to read JSON file: {e}'))
            return
        
        if not keep_existing:
            event_count = Event.objects.count()
            
            if event_count > 0 and not force:
                self.stdout.write(self.style.WARNING(f'This will delete all {event_count} existing events in the database.'))
                confirm = input('Are you sure you want to continue? (y/n): ')
                
                if confirm.lower() != 'y':
                    self.stdout.write(self.style.ERROR('Import canceled.'))
                    return
            
            Event.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {event_count} existing events from the database.'))
            
        landmarks_created = 0
        
        for landmark_data in landmarks:
            landmark = Event(
                title=landmark_data['title'],
                description=landmark_data['description'],
                location_name=landmark_data['location_name'],
                latitude=landmark_data['latitude'],
                longitude=landmark_data['longitude'],
                event_date=timezone.now(),
                created_by=admin_user,
                category=landmark_data['category']
            )
            
            landmark.save()
            landmarks_created += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {landmarks_created} landmarks'))

    def _create_system_user(self):
        """Create a system user for landmarks"""
        system_user = User(
            id=uuid.uuid4(),
            username='system_landmarks',
            first_name='System',
            last_name='Landmarks',
            email='system@eventradar.local',
            password='not_for_login',
            role='User'
        )
        system_user.save()
        self.stdout.write(self.style.SUCCESS('Created system user for landmarks'))
        return system_user 