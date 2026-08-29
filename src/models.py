from django.db import models

class Note(models.Model):

    owner = models.CharField(max_length=80)
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Credential(models.Model):

    username = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username
