
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    """
    model user-->inherits from th AbstructUser model...modify to have field email also adds a 
    profile picture fielf
    """
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    

    REQUIRED_FIELDS = ['username'] 
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
