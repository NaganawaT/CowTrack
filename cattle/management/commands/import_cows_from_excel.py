from django.core.management.base import BaseCommand
from django.conf import settings
import os
import pandas as pd
from datetime import datetime
from cattle.utils import process_excel_file
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

class Command(BaseCommand):
    help = '指定されたディレクトリからExcelファイルを自動インポートします'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            type=str,
            default='./excel_imports',
            help='Excelファイルが格納されているディレクトリのパス'
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            default=True,
            help='重複データをスキップする'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            default=False,
            help='既存データを更新する'
        )
        parser.add_argument(
            '--skip-check-digit',
            action='store_true',
            default=False,
            help='チェックデジット検証をスキップする'
        )
        parser.add_argument(
            '--move-processed',
            action='store_true',
            default=True,
            help='処理済みファイルを移動する'
        )

    def handle(self, *args, **options):
        directory = options['directory']
        skip_duplicates = options['skip_duplicates']
        update_existing = options['update_existing']
        skip_check_digit = options['skip_check_digit']
        move_processed = options['move_processed']

        # ディレクトリが存在しない場合は作成
        if not os.path.exists(directory):
            os.makedirs(directory)
            self.stdout.write(
                self.style.WARNING(f'ディレクトリ {directory} が存在しないため作成しました')
            )
            return

        # 処理済みファイル用のディレクトリ
        processed_dir = os.path.join(directory, 'processed')
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)

        # エラーファイル用のディレクトリ
        error_dir = os.path.join(directory, 'error')
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)

        # Excelファイルを検索
        excel_files = []
        for file in os.listdir(directory):
            if file.endswith(('.xlsx', '.xls')) and not file.startswith('~$'):
                excel_files.append(file)

        if not excel_files:
            self.stdout.write(
                self.style.WARNING(f'ディレクトリ {directory} にExcelファイルが見つかりません')
            )
            return

        self.stdout.write(f'{len(excel_files)}個のExcelファイルを処理します...')

        total_created = 0
        total_updated = 0
        total_skipped = 0
        total_errors = 0

        for filename in excel_files:
            file_path = os.path.join(directory, filename)
            
            try:
                self.stdout.write(f'処理中: {filename}')
                
                # ファイルをDjangoのFileオブジェクトとして扱う
                with open(file_path, 'rb') as f:
                    django_file = File(f, name=filename)
                    
                    # Excelファイルを処理
                    results = process_excel_file(
                        django_file, 
                        skip_duplicates=skip_duplicates, 
                        update_existing=update_existing,
                        skip_check_digit=skip_check_digit
                    )
                
                # 結果を表示
                if results['created'] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'  → {results["created"]}件登録')
                    )
                    total_created += results['created']
                
                if results['updated'] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'  → {results["updated"]}件更新')
                    )
                    total_updated += results['updated']
                
                if results['skipped'] > 0:
                    self.stdout.write(
                        self.style.WARNING(f'  → {results["skipped"]}件スキップ')
                    )
                    total_skipped += results['skipped']
                
                if results['errors']:
                    self.stdout.write(
                        self.style.ERROR(f'  → {len(results["errors"])}件エラー')
                    )
                    total_errors += len(results['errors'])
                    
                    # エラーファイルを移動
                    if move_processed:
                        error_file_path = os.path.join(error_dir, filename)
                        os.rename(file_path, error_file_path)
                        self.stdout.write(f'  → エラーファイルを {error_dir} に移動')
                else:
                    # 成功したファイルを移動
                    if move_processed:
                        processed_file_path = os.path.join(processed_dir, filename)
                        os.rename(file_path, processed_file_path)
                        self.stdout.write(f'  → 処理済みファイルを {processed_dir} に移動')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'ファイル {filename} の処理中にエラーが発生しました: {str(e)}')
                )
                total_errors += 1
                
                # エラーファイルを移動
                if move_processed:
                    error_file_path = os.path.join(error_dir, filename)
                    os.rename(file_path, error_file_path)
                    self.stdout.write(f'  → エラーファイルを {error_dir} に移動')

        # 最終結果を表示
        self.stdout.write('\n' + '='*50)
        self.stdout.write('処理完了')
        self.stdout.write(f'総登録件数: {total_created}')
        self.stdout.write(f'総更新件数: {total_updated}')
        self.stdout.write(f'総スキップ件数: {total_skipped}')
        self.stdout.write(f'総エラー件数: {total_errors}')
        self.stdout.write('='*50) 