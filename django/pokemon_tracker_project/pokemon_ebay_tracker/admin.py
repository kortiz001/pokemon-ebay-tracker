from django.contrib import admin
from .models import EbayAPIKey, SavedItem

admin.site.register(EbayAPIKey)
admin.site.register(SavedItem)