from django.core.management.base import BaseCommand
from cattle.models import Cow
from datetime import date

class Command(BaseCommand):
    help = '本番環境用のサンプルデータを投入します'

    def handle(self, *args, **options):
        # 既存のデータをクリア
        Cow.objects.all().delete()
        
        # サンプルデータを作成
        sample_cows = [
            {
                'cow_number': '1234567890',
                'shed_code': '4101',
                'intake_date': date(2024, 1, 15),
                'gender': 'female',
                'origin_region': '北海道',
                'status': 'active'
            },
            {
                'cow_number': '1234567891',
                'shed_code': '4102',
                'intake_date': date(2024, 2, 20),
                'gender': 'male',
                'origin_region': '曽於',
                'status': 'active'
            },
            {
                'cow_number': '1234567892',
                'shed_code': '4103',
                'intake_date': date(2024, 3, 10),
                'gender': 'castrated',
                'origin_region': '関',
                'status': 'active'
            },
            {
                'cow_number': '1234567893',
                'shed_code': '4201',
                'intake_date': date(2024, 4, 5),
                'gender': 'female',
                'origin_region': '飛騨',
                'status': 'active'
            },
            {
                'cow_number': '1234567894',
                'shed_code': '4202',
                'intake_date': date(2024, 5, 12),
                'gender': 'male',
                'origin_region': '自家',
                'status': 'active'
            },
            {
                'cow_number': '1234567895',
                'shed_code': '1001',
                'intake_date': date(2024, 6, 8),
                'gender': 'female',
                'origin_region': '北海道',
                'status': 'active'
            },
            {
                'cow_number': '1234567896',
                'shed_code': '1002',
                'intake_date': date(2024, 7, 15),
                'gender': 'male',
                'origin_region': '曽於',
                'status': 'active'
            },
            {
                'cow_number': '1234567897',
                'shed_code': '1003',
                'intake_date': date(2024, 8, 22),
                'gender': 'castrated',
                'origin_region': '関',
                'status': 'active'
            },
            {
                'cow_number': '1234567898',
                'shed_code': '2001',
                'intake_date': date(2024, 9, 30),
                'gender': 'female',
                'origin_region': '飛騨',
                'status': 'active'
            },
            {
                'cow_number': '1234567899',
                'shed_code': '2002',
                'intake_date': date(2024, 10, 5),
                'gender': 'male',
                'origin_region': '自家',
                'status': 'active'
            }
        ]
        
        for cow_data in sample_cows:
            Cow.objects.create(**cow_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'成功: {len(sample_cows)}頭の牛データを投入しました')
        ) 