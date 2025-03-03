from django.contrib import admin
from .models import EbayAPIKey, SavedItem, SearchExclusion

admin.site.register(EbayAPIKey)
admin.site.register(SavedItem)
admin.site.register(SearchExclusion)