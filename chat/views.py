from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
from django.conf import settings
import uuid
from .models import Conversation,Message
from django.http import JsonResponse
from openai.types import Model

# Create your views here.


def chat_interface(request):
    return render(request, 'chat_page.html')

def send_prompt_to_openai_chat_api(request):
    if request.method == 'POST':
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if request.session.get('session_id'):
            id=None
            for conv in Conversation.objects.all():
                if request.session.get('session_id')==conv.session_id:
                    id=conv.id
            
            message=Message.objects.create(conversation=Conversation.objects.get(id=id),sender='User',
                                           text=request.POST.get('prompt'))
            response = client.chat.completions.create(
            model=request.POST.get('model'),
            messages=[
            {"role": "user", "content": request.POST.get('prompt')}
            ],
            temperature=0,
            )
            message=Message.objects.create(conversation=Conversation.objects.get(id=id),sender='Chatbot',
                                           text=response.choices[0].message.content)
            return JsonResponse({'bot_answer':response.choices[0].message.content})
            
        else:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            conversation = Conversation.objects.create(session_id=session_id)
            message=Message.objects.create(conversation=Conversation.objects.get(id=conversation.id),sender='User',
                                    text=request.POST.get('prompt'))
            response = client.chat.completions.create(
            model=request.POST.get('model'),
            messages=[
            {"role": "user", "content": request.POST.get('prompt')}
            ],
            temperature=0,
            )
            message=Message.objects.create(conversation=Conversation.objects.get(id=conversation.id),sender='Chatbot',
                                    text=response.choices[0].message.content)
            return JsonResponse({'bot_answer': response.choices[0].message.content})

def end_session(request):
    # Remove session-related data from the session
    id=None
    if 'session_id' in request.session:
        id=request.session['session_id']
        del request.session['session_id']
    return JsonResponse({'session_id': id})

def get_models(request):
    if request.method == 'GET':
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.models.list()
        print(response)
        models_data = [model.id for model in response.data]

        return JsonResponse({'models': models_data})
