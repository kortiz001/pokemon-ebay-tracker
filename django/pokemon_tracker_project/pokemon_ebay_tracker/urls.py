from django.urls import path
from . import views

app_name = 'pokemon_ebay_tracker'

urlpatterns = [
    path('', views.home, name='home'),
    path('tracker/', views.tracker, name='tracker'),
    path('saved/', views.saved, name='saved'),
    path('load_data/', views.load_data, name='load_data'),
    path('delete_saved_item/', views.delete_saved_item, name='delete_saved_item'),
    path('write_saved_item/', views.write_saved_item, name='write_saved_item'),
    path('save_api_key/', views.save_api_key, name='save_api_key'),
]