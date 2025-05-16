from django.urls import path
from .views import CustomAuthToken

urlpatterns = [
        path('login/', CustomAuthToken.as_view(), name='api-login'),
]
