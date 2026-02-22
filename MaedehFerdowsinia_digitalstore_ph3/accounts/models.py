from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    #  فاز ۴ – تایید ایمیل
    is_email_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.username
