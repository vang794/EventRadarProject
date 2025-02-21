from Methods.Login import Login
from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User, Roles
from Methods.Login import Login


class ChangeAccountDetailsAcceptanceTests(TestCase):
    def setUp(self):
        self.client = Client() #create test user
        
        self.user = User.objects.create(
            email = "test@gmail.com",
            username = "testuser",
            first_name = "test",
            last_name = "user",
            password = "password123",
            role = Roles.USER
        )

        session = self.client.session
        session["user_id"] = self.user.username  # Assuming username is the primary key
        session["is_authenticated"] = True  #flag for authentication
        session.save()
        
    def test_user_can_update_email(self):
        response = self.client.post(
            reverse("settings"),
            {"update_email": "1", "email": "email@gmail.com"},
        )
        self.user.refresh_from_db() #refresh from database

        self.assertEqual(self.user.email, "email@gmail.com")
        self.assertEqual(response.status_code, 200) #does not redirect
        self.assertContains(response, "Your email has been updated successfully") 


    # def test_user_cannot_use_duplicate_email(self):
   
    # def test_user_can_update_username(self): #will not work until primary key is changed
    
    # def test_user_gets_error_invalid_username(self):

    # def test_user_sees_error_for_blank_username(self):

    # def test_user_can_update_first_name(self):

    # def test_user_can_update_last_name(self):

    # def test_user_error_blank_first_name(self):
    
    # def test_user_error_blank_last_name(self):
    