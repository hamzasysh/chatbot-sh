from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch
from .models import Conversation, Message
from .views import (
    chat_interface,
    send_prompt_to_openai_chat_api,
    end_session,
    get_models
)

# Create your tests here.

class ChatTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_chat_interface(self):
        request = self.factory.get('/chat-interface/')
        response = chat_interface(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_page.html')

    @patch('chat.views.OpenAI')
    def test_send_prompt_to_openai_chat_api(self, mock_openai):
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        request = self.factory.post('/send-prompt/', {'prompt': 'Test', 'model': 'test_model'})
        response = send_prompt_to_openai_chat_api(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['bot_answer'], 'Test response')
        self.assertTrue(Conversation.objects.exists())
        self.assertTrue(Message.objects.exists())

    def test_end_session(self):
        request = self.factory.post('/end-session/')
        response = end_session(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['session_id'], None)

    @patch('chat.views.OpenAI')
    def test_get_models(self, mock_openai):
        mock_client = mock_openai.return_value
        mock_client.models.list.return_value = {'data': [{'id': 'model1'}, {'id': 'model2'}]}
        request = self.factory.get('/get-models/')
        response = get_models(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'models': ['model1', 'model2']})
