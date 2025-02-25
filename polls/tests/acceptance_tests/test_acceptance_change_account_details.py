from django.test import TestCase, Client
from django.urls import reverse
from polls.models import User



class ChangeAccountDetailsAcceptanceTests(TestCase):
    def setUp(self):
        self.client = Client() #create test user
        
        self.user = User.objects.create(
            email = "test@gmail.com",
            username = "testuser",
            first_name = "Annie",
            last_name = "Harms",
            password = "password123",
        )

        session = self.client.session
        session["user_id"] = str(self.user.id) #login
        session.save()

    
    def test_user_can_update_email(self):
        response = self.client.post(reverse("settings"), { #sends POST request to settings page
            "update_email" : "on",
            "email" : "updated@gmail.com" #new email
        })

        self.user.refresh_from_db() 
        self.assertEqual(self.user.email, "updated@gmail.com") #checks if email was updated
        self.assertRedirects(response, reverse("settings"))  #Redirect on success
    
    
    def test_user_cannot_update_email_to_duplicate(self):
        User.objects.create(username="differentuser", email="testnew@gmail.com", password="pass123")
        response = self.client.post(reverse("settings"), {
            "update_email": "on",
            "email": "testnew@gmail.com"
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "test@gmail.com")
    #     self.assertContains(response, "Failed to update email")
    
    def test_user_can_update_username(self):
        response = self.client.post(reverse("settings"), {
            "update_username": "on",
            "username": "updatedusername1"
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updatedusername1")
        self.assertRedirects(response, reverse("settings"))

    def test_user_cannot_update_username_invalid(self):
        response = self.client.post(reverse("settings"), {
            "update_username": "on",
            "username": "*invalidName"
        })
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, "*invalidName")
    #    self.assertContains(response, "Failed to update username")

    def test_user_can_update_first_name(self):
        response = self.client.post(reverse("settings"), {
            "update_first_name": "on",
            "first_name": "Annie"
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Annie")
        self.assertRedirects(response, reverse("settings"))

    def test_user_can_update_first_name_invalid(self):
        response = self.client.post(reverse("settings"), {
            "update_first_name": "on",
            "first_name": "!invalid"
        })
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, "!invalid")
        #self.assertContains(response, "Failed to update first name")

    def test_update_last_name_success(self):
        response = self.client.post(reverse("settings"), {
            "update_last_name": "on",
            "last_name": "Harms"
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "Harms")
        self.assertRedirects(response, reverse("settings"))

    def test_user_canot_update_last_name_invalid(self):
        response = self.client.post(reverse("settings"), {
            "update_first_name": "on",
            "first_name": "!invalid"
        })
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, "!invalid")
        #self.assertContains(response, "Failed to update last name")

    def test_unauthenticated_user_redirect_to_login_page(self):
        self.client.session.flush()  #logout user
        response = self.client.get(reverse("settings"))
        self.assertRedirects(response, reverse("login"))

    