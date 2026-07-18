from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import os

        if os.environ.get("RENDER_CREATE_SUPERUSER") != "True":
            return

        try:
            from django.contrib.auth.models import User

            username = os.environ.get("SUPERUSER_USERNAME")
            email = os.environ.get("SUPERUSER_EMAIL")
            password = os.environ.get("SUPERUSER_PASSWORD")

            if username and password:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(
                        username=username,
                        email=email,
                        password=password,
                    )
                    print(f"Superuser '{username}' created successfully.")

        except Exception as e:
            print(f"Superuser creation skipped: {e}")