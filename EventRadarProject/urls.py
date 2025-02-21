"""
URL configuration for EventRadarProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from Methods.reset import CustomPasswordResetView
from polls.views import LoginAuth, CreateAcct, SettingPage, sign_out, HomePage

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', LoginAuth.as_view(), name='login'),
    path('create-account/', CreateAcct.as_view(), name='create_account'),
    path('homepage/', HomePage.as_view(), name='homepage'),
    path('settings/', SettingPage.as_view(), name='settings'),
    path('sign_out/', SettingPage.as_view(), name='sign_out'),
    path('admin/', admin.site.urls),

    #Urls for reset password
    path('reset_password/', CustomPasswordResetView.as_view(template_name="password_reset.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), name='password_reset_complete'),

]

