from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = '管理者ユーザーを作成'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='ユーザー名')
        parser.add_argument('--email', type=str, default='admin@example.com', help='メールアドレス')
        parser.add_argument('--password', type=str, default='admin123', help='パスワード')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        # 既存のユーザーを削除
        User.objects.filter(username=username).delete()
        
        # 新しいユーザーを作成
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        
        self.stdout.write(f'管理者ユーザーを作成しました: {username}')
        self.stdout.write(f'ユーザー名: {username}')
        self.stdout.write(f'パスワード: {password}')
        self.stdout.write(f'メール: {email}') 