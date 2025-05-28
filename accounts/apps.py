from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

def ready(self):
    import accounts.signals  # 앱 이름이 accounts라고 가정
