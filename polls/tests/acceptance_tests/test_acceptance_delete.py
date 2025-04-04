from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User, Roles
from django.contrib.auth.hashers import make_password

class DeleteAcceptanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data1 = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': make_password('testpass123'),
            'phone_number': 1234567890,
            'role': Roles.USER
        }

        self.user_data2 = {
            'username': 'testuser2',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test2@example.com',
            'password': make_password('testpass123'),
            'phone_number': 1234567891,
            'role': Roles.USER
        }

        # Create user instance and save to database
        self.user1 = User.objects.create(**self.user_data1)
        self.user2 = User.objects.create(**self.user_data2)


        #User can successfully delete account
    def test_user_can_delete(self):
        self.client.login(username='test@example.com', password='testpass123')
            #User is on the delete home page
            #User session has their email
            #User enters correct email and password and matching confirmation password
            #User is directed to delete_complete page
            #delete_complete page clears session's user
        self.client.session['email']=self.user1.email
        self.client.session['is_authenticated']=True
        self.client.session.save()

        # Submit matching email and password
        data ={
            'email': self.user1.email,
            'password1': 'testpass123',
            'password2': 'testpass123'}
        response = self.client.post(reverse('delete'), data)

            # Check if the session is cleared
        self.assertIsNone(self.client.session.get('email'))
        self.assertIsNone(self.client.session.get('is_authenticated'))


        #User tries to delete other account that is not theirs
    def test_user_cant_delete_other(self):
            #User is on delete page
            #User enters in form with another valid accounts username and password
            #Get error that they can not delete another persons account
            #Logged into user1 account
        self.client.session['email'] = self.user1.email
        self.client.session['is_authenticated'] = True
        self.client.session.save()

            # trying to delete other user's account
        data = {
            'email': self.user2.email,  # Trying to delete user2's account
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('delete'), data)

           #Get the error
        self.assertContains(response, "Incorrect Email")
        self.assertEqual(response.status_code, 200)
