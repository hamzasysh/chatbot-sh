from django.urls import path
from .views import chat_interface,send_prompt_to_openai_chat_api,end_session,get_models

urlpatterns = [
    path('', chat_interface, name='chat_interface'),
    path('send-prompt/',send_prompt_to_openai_chat_api,name='send_prompt'),
    path('end-session/',end_session, name='end_session'),
    path('get-models/', get_models, name='get_models'),

    

]
