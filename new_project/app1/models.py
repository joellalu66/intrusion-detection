from django.db import models

class IntrusionEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='videos/')
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return f"Intrusion Event at {self.timestamp}"

# Create your models here.
