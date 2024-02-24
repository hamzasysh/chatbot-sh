from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
from django.conf import settings
import uuid
from .models import Conversation
from django.http import JsonResponse


# Create your views here.


def chat_interface(request):
    session_id = request.session.get('session_id')
    if not session_id:
        # Generate a new session ID if it doesn't exist
        session_id = str(uuid.uuid4())
        conversation = Conversation.objects.create(session_id=session_id)
        request.session['session_id'] = session_id
    return render(request, 'chat_page.html')

def send_prompt_to_openai_chat_api(request):
    if request.method == 'POST':
        pass
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = request.POST.get('prompt')
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Knock knock."},
        {"role": "assistant", "content": "Who's there?"},
        {"role": "user", "content": "Orange."},
        ],
        temperature=0,
        )

def end_session(request):
    # Remove session-related data from the session
    id=None
    if 'session_id' in request.session:
        id=request.session['session_id']
        del request.session['session_id']
    return JsonResponse({'session_id': id})
