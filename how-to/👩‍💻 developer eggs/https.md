# HTTPS 4 WSS (secure http for secure websocket) in `WIN 田`
*Starting development Django server at `https`*

> requirements `python3.11`

```bash
python -m pip install django-sslserver
```

* Add the application to your `INSTALLED_APPS`:

    ```python
    INSTALLED_APPS = (
        ...
        "sslserver",
        ...
    )
    ```

* Start a SSL-enabled debug server at default port `8000`:

    ```bash
    python manage.py runsslserver
    ```

* Start a SSL-enabled debug server at port `9000`:

    ```bash
    python manage.py runsslserver 127.0.0.1:9000
    ```


## Credits

[teddziuba/django-sslserver](https://github.com/teddziuba/django-sslserver)