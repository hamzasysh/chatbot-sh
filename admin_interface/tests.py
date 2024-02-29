from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .views import admin_interface
from .forms import TrainingForm

# Create your tests here.

class AdminInterfaceViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('admin_interface.views.OpenAI')
    @patch('admin_interface.views.create_fine_tuning_file')
    @patch('admin_interface.views.fine_tune_model')
    @patch('admin_interface.views.load_db_conversations_in_csv')
    @patch('admin_interface.views.load_csv_finetuning')
    @patch('admin_interface.views.merge_jsonl')
    def test_admin_interface_post_valid_form(self, mock_merge_jsonl, mock_load_csv_finetuning, 
                                              mock_load_db_conversations_in_csv, mock_fine_tune_model, 
                                              mock_create_fine_tuning_file, mock_openai):
        mock_openai_instance = MagicMock()
        mock_openai_instance.files.create.return_value.id = 'file_id'
        mock_openai_instance.fine_tuning.jobs.create.return_value.fine_tuned_model = 'fine_tuned_model'
        mock_openai.return_value = mock_openai_instance

        form_data = {'file': 'fake_file_content'}
        request = self.factory.post('/admin-interface/', form_data)
        request.FILES['file'] = 'fake_file_content'
        response = admin_interface(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['form'])
        self.assertEqual(response.context['success_message'], 'Training has completed successfully, Fine-tuned Model is : fine_tuned_model')

        # Add assertions for file operations and API calls

    def test_admin_interface_post_invalid_form(self):
        invalid_form_data = {'file': 'fake_file_content'}
        request = self.factory.post('/admin-interface/', invalid_form_data)
        response = admin_interface(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertEqual(response.context['success_message'], 'Training has failed')

    def test_admin_interface_get(self):
        request = self.factory.get('/admin-interface/')
        response = admin_interface(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertIsNone(response.context['success_message'])
