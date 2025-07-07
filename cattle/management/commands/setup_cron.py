from django.core.management.base import BaseCommand
import os
import subprocess
from datetime import datetime

class Command(BaseCommand):
    help = 'Excelファイルの自動インポート用のcronジョブを設定します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schedule',
            type=str,
            default='0 */6 * * *',  # 6時間ごと
            help='cronスケジュール（デフォルト: 6時間ごと）'
        )
        parser.add_argument(
            '--directory',
            type=str,
            default='./excel_imports',
            help='Excelファイルが格納されているディレクトリのパス'
        )
        parser.add_argument(
            '--log-file',
            type=str,
            default='./logs/excel_import.log',
            help='ログファイルのパス'
        )

    def handle(self, *args, **options):
        schedule = options['schedule']
        directory = options['directory']
        log_file = options['log_file']

        # ログディレクトリを作成
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            self.stdout.write(f'ログディレクトリ {log_dir} を作成しました')

        # プロジェクトディレクトリを取得
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # manage.pyのパス
        manage_py = os.path.join(project_dir, 'manage.py')
        
        # cronジョブのコマンド
        cron_command = f'{schedule} cd {project_dir} && python {manage_py} import_cows_from_excel --directory={directory} >> {log_file} 2>&1'
        
        # 現在のcrontabを取得
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_crontab = result.stdout
        except subprocess.CalledProcessError:
            current_crontab = ""

        # 既存のジョブを削除（同じコマンドがある場合）
        lines = current_crontab.split('\n')
        filtered_lines = []
        for line in lines:
            if 'import_cows_from_excel' not in line and line.strip():
                filtered_lines.append(line)

        # 新しいジョブを追加
        new_crontab = '\n'.join(filtered_lines) + '\n' + cron_command + '\n'

        # crontabを更新
        try:
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)
            
            if process.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS('cronジョブが正常に設定されました')
                )
                self.stdout.write(f'スケジュール: {schedule}')
                self.stdout.write(f'ディレクトリ: {directory}')
                self.stdout.write(f'ログファイル: {log_file}')
            else:
                self.stdout.write(
                    self.style.ERROR('cronジョブの設定に失敗しました')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'cronジョブの設定中にエラーが発生しました: {str(e)}')
            )

        # 手動設定用の情報を表示
        self.stdout.write('\n' + '='*50)
        self.stdout.write('手動でcronジョブを設定する場合:')
        self.stdout.write('1. crontab -e を実行')
        self.stdout.write('2. 以下の行を追加:')
        self.stdout.write(f'   {cron_command}')
        self.stdout.write('='*50) 