# Configuring UTF8 Character Set for MySQL
``` sql
CREATE DATABASE BPARTS_DB character set utf8mb4 collate utf8mb4_general_ci
```

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

# Confirm if the DBs were created

To confirm whether the databases exist, you can use the MySQL command-line client or a MySQL GUI tool such as phpMyAdmin or MySQL Workbench. Here's how you can check using the command-line client:

1. Open a terminal or command prompt.

2. Log in to your MySQL server using the MySQL command-line client. Replace 'your_database_user' with your MySQL username:

```bash
mysql -u <your_database_user> -p
```

Once logged in, you can list the databases using the following command:

```sql
SHOW DATABASES;
```

This will display a list of all databases on your MySQL server.

Look for the database(s) you specified in your Django settings. If you used a placeholder name, you should see that database listed.

If you provided an actual database name and it doesn't appear in the list, it means Django wasn't able to create it. You may need to troubleshoot your Django settings or MySQL configuration.

To exit the MySQL command-line client, type:

```sql
    exit;
```
> Then press **Enter ↵**.

By following these steps, you can confirm whether the databases you specified in your Django settings exist on your MySQL server. If they do, it means Django was able to create them successfully during the migration process. If not, you may need to troubleshoot and adjust your Django settings or MySQL configuration accordingly.
