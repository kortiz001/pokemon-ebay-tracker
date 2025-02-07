from django.urls import path
from . import views

app_name = 'pokemon_ebay_tracker'

urlpatterns = [
    path('', views.home, name='home'),  # Homepage view
    path('load_data/', views.load_data, name='load_data'),  # AJAX data request
]