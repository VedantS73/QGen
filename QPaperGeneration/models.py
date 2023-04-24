from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser): 
    pass

class Subject(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return f"{self.name}"
    
class Topic(models.Model):
    name = models.CharField(max_length=32)
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject')
    def __str__(self):
        return f"{self.sub} : {self.name}"
    
class QPattern(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usr")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topic')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sub', default=0)
    imgurl = models.CharField(max_length=128, blank=True)
    question = models.TextField(default="N/A")
    answer = models.TextField(default="N/A",blank=True)
    marks = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=1)
    co = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.topic} : {self.question}"
