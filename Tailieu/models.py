from django.db import models  # Correct import for SQL databases

class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email
