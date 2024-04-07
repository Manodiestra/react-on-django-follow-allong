from django.contrib import admin
from .models import JournalEntry, CustomUser

admin.site.register(JournalEntry)
admin.site.register(CustomUser)
