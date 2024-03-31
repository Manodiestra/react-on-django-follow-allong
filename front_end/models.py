from django.db import models

from django.db import models

class JournalEntry(models.Model):
    user_id = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    content = models.TextField()
    dateTime = models.DateTimeField()

# Remember to make migrations after changing this file!
#
# python manage.py makemigrations
# python manage.py migrate
