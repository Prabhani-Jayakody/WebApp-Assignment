from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        default='default.jpg', 
        upload_to='profile_pics', 
        null=True, 
        blank=True
    )
    bio = models.TextField(max_length=500, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    address = models.CharField(max_length=200, blank=True, default='')
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.profile_picture and self.profile_picture.name != 'default.jpg':
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_picture.path)
            except Exception as e:
                print(f"Error processing image: {e}")