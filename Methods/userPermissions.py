from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist

from Methods.SessionLoginMixin import SessionLoginRequiredMixin
from polls.models import User


#check if adminn
#check that the user is an admin or manager
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from Methods.SessionLoginMixin import SessionLoginRequiredMixin
from polls.models import User


class RoleRequiredMixin(SessionLoginRequiredMixin):
    required_role = []
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # User must be logged in
        if not request.session.get("email") and not request.session.get("is_authenticated"):
            return redirect("login")

        # User must be of required role
        email=request.session.get("email")
        user=User.objects.get(email=email)
        if self.required_role and user.role not in self.required_role:
            return redirect("homepage")  # Redirect if the user doesn't have the required role
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(RoleRequiredMixin):
    required_role = ["Admin"]
class EventManagerRequiredMixin(RoleRequiredMixin):
    required_role = ["Event Manager"]
class AdminManagerRequiredMixin(RoleRequiredMixin):
    required_role = ["Admin", "Event Manager"]
class UserRequiredMixin(RoleRequiredMixin):
    required_role = ["Admin","User"]