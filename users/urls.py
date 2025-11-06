from django.conf import settings
from django.urls import  path, re_path

from rest_framework_simplejwt.views import TokenVerifyView

from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from dj_rest_auth.jwt_auth import get_refresh_view

from .views import UserDestroyView


app_name = 'users'


urlpatterns = [
    path('', RegisterView.as_view(), name='rest_register'),
    re_path(r'login/?$', LoginView.as_view(), name='rest_login'),
    # URLs that require a user to be logged in with a valid session / token.
    re_path(r'logout/?$', LogoutView.as_view(), name='rest_logout'),
    re_path(r'user/?$', UserDetailsView.as_view(), name='rest_user_details'),
    re_path(r'token/verify/?$', TokenVerifyView.as_view(), name='token_verify'),
    re_path(r'token/refresh/?$', get_refresh_view().as_view(), name='token_refresh'),

    path('api/users/<int:id>/delete/', UserDestroyView.as_view(), name='user-delete'),

]
