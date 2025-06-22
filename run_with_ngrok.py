#!/usr/bin/env python
"""
ngrokを使用してDjangoサーバーを外部公開するスクリプト
"""

import os
import sys
import django
from pyngrok import ngrok
from django.core.management import execute_from_command_line

def main():
    # Django設定を読み込み
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CowTrack.settings')
    django.setup()
    
    # ngrokトンネルを作成
    print("ngrokトンネルを作成中...")
    public_url = ngrok.connect("8000")
    print(f"外部アクセスURL: {public_url}")
    print("このURLを他の人に共有してアクセス可能です")
    print("Ctrl+Cで終了")
    
    try:
        # Djangoサーバーを起動
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\nngrokトンネルを終了中...")
        ngrok.kill()
        print("終了しました")

if __name__ == '__main__':
    main() 