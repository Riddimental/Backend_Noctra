from django.apps import AppConfig


class NoctraAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'noctra_app'

    def ready(self):
        import noctra_app.signals