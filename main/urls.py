from django.urls import path
from main.views import verify_user, challenge_result, register_user

urlpatterns = [
    path('verify_user', verify_user, name='verify_user'),
    path('challenge_result', challenge_result, name='challenge_result'),
    path('register_user', register_user, name='register_user'),
]
