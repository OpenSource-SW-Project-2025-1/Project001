from django.apps import AppConfig
from django.core.management import call_command

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

from django.db.models.signals import post_migrate

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import os
        # 서버 실행 시에만 migrate 하도록 제한 (관리 명령어 실행 시 제외)
        if os.environ.get('RUN_MAIN') == 'true':  # runserver 재시작 구분용
            try:
                call_command('migrate', interactive=False)
            except Exception as e:
                print(f"[자동 마이그레이션 실패] {e}")

    def ready(self):
        from . import signals
        post_migrate.connect(signals.load_location_data, sender=self)


