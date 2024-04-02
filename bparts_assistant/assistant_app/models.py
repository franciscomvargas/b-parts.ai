from django.db import models

'''
Explanation of the models:

    User: Represents the users in your application. It has three fields:
        user_id: Auto-incrementing primary key for each user.
        assistant_id: Foreign key linking to the Admin table, representing the assistant assigned to the user.
        assistant_thread_id: A JSONField to store a list of strings representing assistant thread IDs.

    Admin: Represents the administrators or assistants in your application. It has three fields:
        assistant_id: Auto-incrementing primary key for each admin.
        assistant_active: Boolean field indicating whether the assistant is active or not (banned).
        assistant_meta: Text field to store conversation or any other metadata related to the assistant.

After defining the models, you need to create migrations and apply them to your database.

In your terminal, navigate to the root directory of your Django project (bparts_assistant) and run the following commands:

```bash
python manage.py makemigrations
python manage.py migrate
```

These commands will create the necessary database migrations based on your models and apply them to your MariaDB database.

Now, your models are synchronized with your database, and you can start using them in your Django project.
'''

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    assistant_id = models.ForeignKey('Admin', on_delete=models.CASCADE)
    assistant_thread_id = models.JSONField(default=list)

class Admin(models.Model):
    assistant_id = models.AutoField(primary_key=True)
    assistant_active = models.BooleanField(default=True)
    assistant_meta = models.TextField(blank=True, null=True)
