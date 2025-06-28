from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = '全ユーザーにis_staff=Trueを付与'

    def handle(self, *args, **options):
        User = get_user_model()
        for user in User.objects.all():
            if not user.is_staff:
                user.is_staff = True
                user.save()
                self.stdout.write(f'Staff権限を付与: {user.username}')
            else:
                self.stdout.write(f'既にStaff: {user.username}') 