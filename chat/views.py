from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.


def chat_interface(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        # Implement logic to process the message and generate a response
        # For demonstration, let's echo the user's message as the bot's response
        return JsonResponse({'response': message})
    return render(request, 'chat_page.html')
