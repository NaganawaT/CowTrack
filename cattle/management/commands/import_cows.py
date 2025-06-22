from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from cattle.models import Cow
import csv
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'CSVファイルから牛データを一括インポートします'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='インポートするCSVファイルのパス')
        parser.add_argument(
            '--update',
            action='store_true',
            help='既存のデータを更新する（指定しない場合は新規作成のみ）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='実際にはデータベースに保存せず、処理内容のみ表示',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        update_existing = options['update']
        dry_run = options['dry_run']

        if not os.path.exists(csv_file):
            raise CommandError(f'CSVファイルが見つかりません: {csv_file}')

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                success_count = 0
                update_count = 0
                error_count = 0
                errors = []

                for row_num, row in enumerate(reader, start=2):  # ヘッダー行を除いて2から開始
                    try:
                        # 必須フィールドのチェック
                        if not row.get('cow_number'):
                            raise ValueError('牛番号が指定されていません')
                        if not row.get('shed_code'):
                            raise ValueError('牛舎番号が指定されていません')
                        if not row.get('intake_date'):
                            raise ValueError('導入日が指定されていません')

                        # 日付の変換
                        try:
                            intake_date = datetime.strptime(row['intake_date'], '%Y-%m-%d').date()
                        except ValueError:
                            raise ValueError('導入日の形式が正しくありません（YYYY-MM-DD形式で入力してください）')

                        # 既存データのチェック
                        existing_cow = Cow.objects.filter(cow_number=row['cow_number']).first()

                        if existing_cow:
                            if update_existing:
                                if not dry_run:
                                    existing_cow.shed_code = row['shed_code']
                                    existing_cow.intake_date = intake_date
                                    existing_cow.gender = row.get('gender', 'female')
                                    existing_cow.origin_region = row.get('origin_region', '自家')
                                    existing_cow.status = row.get('status', 'active')
                                    existing_cow.save()
                                update_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f'更新: {row["cow_number"]} ({row["shed_code"]})')
                                )
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f'スキップ: {row["cow_number"]} (既存データ)')
                                )
                        else:
                            if not dry_run:
                                Cow.objects.create(
                                    cow_number=row['cow_number'],
                                    shed_code=row['shed_code'],
                                    intake_date=intake_date,
                                    gender=row.get('gender', 'female'),
                                    origin_region=row.get('origin_region', '自家'),
                                    status=row.get('status', 'active'),
                                )
                            success_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'作成: {row["cow_number"]} ({row["shed_code"]})')
                            )

                    except Exception as e:
                        error_count += 1
                        error_msg = f'行 {row_num}: {str(e)}'
                        errors.append(error_msg)
                        self.stdout.write(
                            self.style.ERROR(error_msg)
                        )

                # 結果の表示
                self.stdout.write('\n' + '='*50)
                self.stdout.write('インポート結果:')
                self.stdout.write(f'新規作成: {success_count}件')
                if update_existing:
                    self.stdout.write(f'更新: {update_count}件')
                self.stdout.write(f'エラー: {error_count}件')
                
                if dry_run:
                    self.stdout.write(self.style.WARNING('※ ドライランモードのため、実際にはデータベースに保存されていません'))
                
                if errors:
                    self.stdout.write('\nエラー詳細:')
                    for error in errors[:10]:  # 最初の10件のエラーのみ表示
                        self.stdout.write(f'  {error}')
                    if len(errors) > 10:
                        self.stdout.write(f'  ... 他 {len(errors) - 10}件のエラー')

        except Exception as e:
            raise CommandError(f'CSVファイルの処理中にエラーが発生しました: {str(e)}') 