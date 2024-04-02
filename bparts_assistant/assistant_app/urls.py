# assistant_app/urls.py
from django.urls import path
from .views import chat_view
from .views import hello_world

urlpatterns = [
    path('', chat_view, name='chat'),  # URL pattern for the chat view
    path('hello/', hello_world, name='hello'),
]
