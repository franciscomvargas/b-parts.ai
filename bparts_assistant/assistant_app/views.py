# views.py
from django.shortcuts import render
from .forms import ChatForm
from django.http import HttpResponse

def chat_view(request):
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            print(message)
            # Process the message here, send it to your OpenAI API, etc.
    else:
        form = ChatForm()

    # Return "bananas" as the response
    return render(request, 'assistant_app/chat.html', {'form': form, 'message': 'bananas'})

def hello_world(request):
    print('** HELLO COCKIE **')
    return HttpResponse("✋ Hello, world! 🌎")