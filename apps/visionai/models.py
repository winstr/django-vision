from django.db import models


class WebsocketHost(models.Model):

    host_uri = models.CharField(max_length=30)
    alias = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.alias
