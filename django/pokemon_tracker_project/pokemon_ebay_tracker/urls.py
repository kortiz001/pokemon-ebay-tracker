from django.urls import path
from . import views

app_name = 'pokemon_ebay_tracker'

urlpatterns = [
    path('', views.home, name='home'),
]