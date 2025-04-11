from django.test import TestCase
from polls.models import User
from Methods.change_account_details import change_account_details

class ChangeAccountDetailsTest(TestCase):

    #create test user
    def setUp(self):
        self.user = User.objects.create(
            email = "test@gmail.com",
            username = "testuser",
            first_name = "test",
            last_name =  "user",
        )
   
    # test email duplicate
    def test_email_duplicate(self):
        User.objects.create(email = "duplicate@gmail.com", username = "testusername") #adds new user to database
        result = change_account_details(self.user, new_email = "duplicate@gmail.com") #attempts to assign user's email to new user
        self.assertFalse(result) #should return false

    #test email success
    def test_email_success(self):
        result = change_account_details(self.user, new_email = "newemail@gmail.com")
        self.assertTrue(result) #should return true
    
    #test email invalid
    def test_email_invalid(self):
        result = change_account_details(self.user, new_email = "invalid-email") 
        self.assertFalse(result)
    
    #test username already exisits
    def test_username_duplicate(self):
        User.objects.create(username = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_username = "testuser2")
        self.assertFalse(result)

    #test blank username is entered
    def test_username_blank(self):
        User.objects.create(username = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_username = " ")
        self.assertFalse(result)

    #test username length < 3 
    def test_username_under_min_length(self):
        User.objects.create(username = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_username = "ab")
        self.assertFalse(result)

    #test > 20
    def test_username_over_max_length(self):
        User.objects.create(username = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_username = "iAmMoreThan20characters")
        self.assertFalse(result)

    #test only letters, numbers and underscores entered
    def test_username_is_all_letters(self):
        User.objects.create(username = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_username = "abc*")
        self.assertFalse(result)
    
    #come back to this one-------------------------------------------------------------------------------------
    #will work once primary key is changed and not username 
    
    #test username success 
    def test_username_success(self):
         self.user.email = "annaliseharms@example.com"
         self.user.save()
         result = change_account_details(self.user, new_username = "happy123")
         self.assertTrue(result)
    
    #test if first_name is blank
    def test_first_name_blank(self):
        User.objects.create(first_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_first_name = " ")
        self.assertFalse(result)
    
    #test first name length < 3
    def test_first_name_blank(self):
        User.objects.create(first_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_first_name = "ab")
        self.assertFalse(result)

    #test first name lenth > 20
    def test_first_name_blank(self):
        User.objects.create(first_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_first_name = "iAmMoreThan20characters")
        self.assertFalse(result)

    #test first name is only letters
    def test_first_name_blank(self):
        User.objects.create(first_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_first_name = "*mmm")
        self.assertFalse(result)

    #test first name success
    def test_first_name_blank(self):
        User.objects.create(first_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_first_name = "Annie")
        self.assertTrue(result)

    #test if last_name is blank
    def test_last_name_blank(self):
        User.objects.create(last_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_last_name = " ")
        self.assertFalse(result)
    
    #test last name length < 3
    def test_last_name_blank(self):
        User.objects.create(last_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_last_name = "ab")
        self.assertFalse(result)

    #test last name lenth > 20
    def test_last_name_blank(self):
        User.objects.create(last_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_last_name = "iAmMoreThan20characters")
        self.assertFalse(result)

    #test last name is only letters
    def test_last_name_blank(self):
        User.objects.create(last_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_last_name = "*mmm")
        self.assertFalse(result)

    #test last name success
    def test_last_name_blank(self):
        User.objects.create(last_name = "testuser2", email = "user2@gmail.com")
        result = change_account_details(self.user, new_last_name = "Annie")
        self.assertTrue(result)