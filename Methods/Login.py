from polls.models import User

class Login:
    def authenticate(self, email, password):
        if self.checkemail(email):
            return self.checkpassword(email, password)
        else:
            return None

    def checkpassword(self, email, password):
        try:
            user = User.objects.get(id=email)  # Fetch user by ID
            if user.password == password:  # Check if the password matches
                return True
        except User.DoesNotExist:
            return False  # User not found
        return False  # Password mismatch

    def checkemail(self, email):
        return User.objects.filter(id=email).exists()  # Check if email/user exists
