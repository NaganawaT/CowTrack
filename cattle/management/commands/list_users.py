from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'ユーザー一覧を表示'

    def handle(self, *args, **options):
        User = get_user_model()
        for user in User.objects.all():
            self.stdout.write(f'username: {user.username}, email: {user.email}, is_superuser: {user.is_superuser}') 