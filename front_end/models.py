from django.db import models
from django.contrib.auth.models import AbstractUser


class JournalEntry(models.Model):
    user_id = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    content = models.TextField()
    dateTime = models.DateTimeField()


class CustomUser(AbstractUser):
    @classmethod
    def get_or_create_for_cognito(cls, jwt_payload):
        """
        This method finds or creates a user based on the JWT payload from AWS Cognito.
        The 'sub' claim in the payload is used as a unique identifier for the user.
        """
        cognito_id = jwt_payload['sub']  # 'sub' is the standard subject claim from Cognito
        user, created = cls.objects.get_or_create(username=cognito_id)

        # If the user was created, you might want to set additional fields from the JWT payload
        if created:
            user.email = jwt_payload.get('email')
            # Set other fields if needed
            user.save()

        return user


# Remember to make migrations after changing this file!
#
# python manage.py makemigrations
# python manage.py migrate
