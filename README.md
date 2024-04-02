# B-Parts AI assistent
Developing an AI assistant dedicated to motorized vehicles using Django.

## 🧠 1st Brainstorm (`chat` with sensei openAI 🙄)

1. **Setting up Django**: Create a new Django project using the command:
    ```
    django-admin startproject bparts_assistant
    ```

2. **Create Django App**: You should create a Django app within your project to contain the logic related to the AI assistant. You can do this using the command:
    ```
    python manage.py startapp assistant_app
    ```

3. **Integrate OpenAI API**: You can start by integrating the OpenAI API within your Django app to enable the AI capabilities. Check [OpenAI documentation](https://platform.openai.com/docs/api-reference) to understand how to make API requests and handle responses.

4. **Design Database Models**: Consider creating Django models to store data related to motorized vehicles, user interactions, and any other relevant information needed for the assistant.

5. **Implement Views and Templates**: Create views that interact with the OpenAI API and serve the appropriate responses to users. Design templates to display the AI assistant's responses on the front end.

6. **Set Up User Authentication**: If you want to enable user-specific features or save user preferences.

### Integrate OpenAI API
```
python -m pip install openai
```

1. **Make API Requests**:
   - Create a function or class in your Django app that interacts with the OpenAI API.
   - Here's a simple example to request completion from OpenAI's GPT-3 model:
     ```python
     import openai

     def get_openai_response(prompt):
         api_key = 'your_api_key_here'
         openai.api_key = api_key
         
         response = openai.Completion.create(
             engine="text-davinci-003",
             prompt=prompt,
             max_tokens=150
         )
         
         return response.choices[0].text.strip()
     ```

4. **Call the OpenAI Function**:
   - After creating the function to interact with the OpenAI API in your Django app, you can now call this function where you need to generate AI responses.
   - You can call the `get_openai_response` function we defined earlier with a prompt and handle the response.

```python
# Assuming you have a view where you take user input and pass it to OpenAI for a response

from django.http import HttpResponse
from .utils import get_openai_response

def assist_user(request):
    user_input = request.POST.get('user_input')
    assistant_response = get_openai_response(user_input)
    
    # You can then render a template or return the response to the user
    return HttpResponse(assistant_response)
```

5. **Further Refinement**:
   - You can optimize the function to handle exceptions, error handling, and additional parameters based on your project requirements.
   - Consider implementing caching mechanisms to reduce API calls and improve performance.

6. **Testing**:
   - Test your integration thoroughly to ensure it works as expected. You can use Django's built-in testing framework or tools like Postman for API testing.