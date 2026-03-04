from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Admin'),
        (2, 'Doctor'),
        (3, 'Patient'),
    )
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=1)

    def __str__(self):
        return self.username
