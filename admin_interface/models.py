from django.db import models

# Create your models here.
class TrainingFile(models.Model):
    file = models.FileField(upload_to='training/')