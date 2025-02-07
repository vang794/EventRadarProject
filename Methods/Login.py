from polls.models import User

class Login:
    def authenticate(self, email, password):
        if self.checkemail(email):
            return self.checkpassword(email, password)
        return None

    def checkpassword(self, email, password):
        try:
            user = User.objects.get(email=email)  # Fetch user by email
            return user.password == password  # Return True if password matches
        except User.DoesNotExist:
            return False  # Return False if user is not found

    def checkemail(self, email):
        return User.objects.filter(email=email).exists()  # Check if email/user exists

    def isBlank(self,email,password):
        # Check if fields are blank
        if not email:
            return False
        if not password:
            return False
