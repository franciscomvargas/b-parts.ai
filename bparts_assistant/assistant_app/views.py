# views.py
from django.shortcuts import render
from .forms import ChatForm
from django.http import HttpResponse

def chat_view(request):
    print('** HELLO MFLIPPA **')
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            print(message)
            # Process the message here, send it to your OpenAI API, etc.
    else:
        form = ChatForm()
    return render(request, 'assistant_app/chat.html', {'form': form})


def hello_world(request):
    print('** HELLO COCKIE **')
    return HttpResponse("✋ Hello, world! 🌎")