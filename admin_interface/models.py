from django.db import models
from django.conf import settings

# Create your models here.
class TrainingFile(models.Model):
    file = models.FileField(upload_to=settings.TRAIN_FOLDER,max_length=1000)