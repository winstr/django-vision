from django.db import models


class Question(models.Model):
    content = models.CharField(max_length=200)
    published_date = models.DateTimeField('date published')

    def __str__(self):
        return self.content


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.content
