from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


class SessionLoginRequiredMixin:
    #Custom mixin that checks if user is of the same email
    #replaces loginmixin
    #https://hyperskill.org/learn/step/51038
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("email") and not request.session.get("is_authenticated"):  # Check if user email is stored in session
            return redirect("login")  # Redirect to login page if not logged in
        return super().dispatch(request, *args, **kwargs)