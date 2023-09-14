from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=20, unique=True)  # Ensure the field is unique

    def __str__(self):
        return self.user.username
 