from django.core.management.base import BaseCommand
from cattle.models import Medicine

class Command(BaseCommand):
    help = '薬剤マスタにサンプルデータを追加します'

    def handle(self, *args, **options):
        medicines_data = [
            {
                'name': 'アンピシリン',
                'default_days': 7,
                'notes': '抗生物質、細菌感染症の治療'
            },
            {
                'name': 'ペニシリン',
                'default_days': 5,
                'notes': '抗生物質、グラム陽性菌感染症の治療'
            },
            {
                'name': 'ストレプトマイシン',
                'default_days': 10,
                'notes': '抗生物質、結核菌感染症の治療'
            },
            {
                'name': 'テトラサイクリン',
                'default_days': 7,
                'notes': '抗生物質、広域スペクトラム'
            },
            {
                'name': 'イブプロフェン',
                'default_days': 3,
                'notes': '解熱鎮痛剤、発熱・疼痛の緩和'
            },
            {
                'name': 'アセトアミノフェン',
                'default_days': 3,
                'notes': '解熱鎮痛剤、副作用が少ない'
            },
            {
                'name': 'ビタミンB群',
                'default_days': 14,
                'notes': 'ビタミン剤、栄養補給'
            },
            {
                'name': 'ビタミンC',
                'default_days': 7,
                'notes': 'ビタミン剤、免疫力向上'
            },
            {
                'name': 'カルシウム剤',
                'default_days': 10,
                'notes': 'ミネラル剤、骨格強化'
            },
            {
                'name': 'プロバイオティクス',
                'default_days': 21,
                'notes': '整腸剤、腸内環境改善'
            }
        ]

        created_count = 0
        for medicine_data in medicines_data:
            medicine, created = Medicine.objects.get_or_create(
                name=medicine_data['name'],
                defaults={
                    'default_days': medicine_data['default_days'],
                    'notes': medicine_data['notes']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'薬剤 "{medicine.name}" を作成しました')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'薬剤 "{medicine.name}" は既に存在します')
                )

        self.stdout.write(
            self.style.SUCCESS(f'合計 {created_count} 件の薬剤を追加しました')
        ) 