from django.db import models

# Create your models here.

class Conversation(models.Model):
    session_id = models.CharField(max_length=100,unique=True)  # Unique identifier for the conversation session

    def __str__(self):
        return self.session_id

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.CharField(max_length=100)  # 'User' or 'Chatbot'
    text = models.TextField()

    def __str__(self):
        return f"{self.sender}: {self.text}"
