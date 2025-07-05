from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import csv
from datetime import datetime
from .models import Veterinarian, Cow, Medicine, Treatment, TreatmentMedicine, DailyVeterinarian, FeedingObservation, TreatmentResult, MovementLog, FollowUpObservation

# User関連のadmin登録は削除・コメントアウト
# from .models import User
# from django.contrib.auth.admin import UserAdmin
# admin.site.register(User, UserAdmin)

@admin.register(Veterinarian)
class VeterinarianAdmin(admin.ModelAdmin):
    list_display = ['name', 'license_number_display', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'license_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    def license_number_display(self, obj):
        return obj.license_number if obj.license_number else '未設定'
    license_number_display.short_description = '獣医師免許番号'

@admin.register(Cow)
class CowAdmin(admin.ModelAdmin):
    list_display = ('id', 'cow_number', 'shed_code', 'gender', 'intake_date', 'origin_region', 'status')
    list_filter = ['status', 'origin_region', 'shed_code']
    search_fields = ['cow_number']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='cattle_cow_import_csv'),
            path('export-csv/', self.export_csv, name='cattle_cow_export_csv'),
        ]
        return custom_urls + urls
    
    def import_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if csv_file:
                try:
                    # CSVファイルをデコード
                    decoded_file = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    
                    success_count = 0
                    error_count = 0
                    errors = []
                    
                    for row in reader:
                        try:
                            # 日付の変換
                            intake_date = datetime.strptime(row['intake_date'], '%Y-%m-%d').date()
                            
                            # 牛の作成
                            cow, created = Cow.objects.get_or_create(
                                cow_number=row['cow_number'],
                                defaults={
                                    'shed_code': row['shed_code'],
                                    'intake_date': intake_date,
                                    'gender': row.get('gender', 'female'),
                                    'origin_region': row.get('origin_region', '自家'),
                                    'status': row.get('status', 'active'),
                                }
                            )
                            
                            if created:
                                success_count += 1
                            else:
                                # 既存データの更新
                                cow.shed_code = row['shed_code']
                                cow.intake_date = intake_date
                                cow.gender = row.get('gender', 'female')
                                cow.origin_region = row.get('origin_region', '自家')
                                cow.status = row.get('status', 'active')
                                cow.save()
                                success_count += 1
                                
                        except Exception as e:
                            error_count += 1
                            errors.append(f"行 {reader.line_num}: {str(e)}")
                    
                    if success_count > 0:
                        messages.success(request, f'{success_count}件の牛データを登録/更新しました。')
                    if error_count > 0:
                        messages.warning(request, f'{error_count}件のエラーが発生しました。')
                        for error in errors[:5]:  # 最初の5件のエラーのみ表示
                            messages.error(request, error)
                    
                except Exception as e:
                    messages.error(request, f'CSVファイルの処理中にエラーが発生しました: {str(e)}')
            else:
                messages.error(request, 'CSVファイルが選択されていません。')
            
            return redirect('..')
        
        return render(request, 'admin/cattle/cow/import_csv.html')
    
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="cows.csv"'
        
        # BOMを追加してExcelで文字化けしないようにする
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow(['cow_number', 'shed_code', 'intake_date', 'gender', 'origin_region', 'status'])
        
        cows = Cow.objects.all()
        for cow in cows:
            writer.writerow([
                cow.cow_number,
                cow.shed_code,
                cow.intake_date.strftime('%Y-%m-%d'),
                cow.gender,
                cow.origin_region,
                cow.status,
            ])
        
        return response

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['cow', 'veterinarian', 'primary_doctor', 'treatment_date', 'diagnosis', 'treatment_type']
    list_filter = ['treatment_date', 'veterinarian', 'primary_doctor', 'treatment_type']
    search_fields = ['cow__cow_number', 'diagnosis', 'veterinarian__name']

@admin.register(TreatmentMedicine)
class TreatmentMedicineAdmin(admin.ModelAdmin):
    list_display = ['treatment', 'medicine', 'dosage_days']

@admin.register(FeedingObservation)
class FeedingObservationAdmin(admin.ModelAdmin):
    list_display = ['cow', 'observer', 'observed_at', 'appetite']
    list_filter = ['observed_at', 'appetite', 'observer']
    search_fields = ['cow__cow_number']

@admin.register(MovementLog)
class MovementLogAdmin(admin.ModelAdmin):
    list_display = ['cow', 'from_shed_code', 'to_shed_code', 'moved_at', 'moved_by']
    list_filter = ['moved_at', 'moved_by']

@admin.register(FollowUpObservation)
class FollowUpObservationAdmin(admin.ModelAdmin):
    list_display = ['treatment', 'observed_at', 'observer', 'appetite']
    list_filter = ['observed_at', 'appetite']

@admin.register(DailyVeterinarian)
class DailyVeterinarianAdmin(admin.ModelAdmin):
    list_display = ['date', 'veterinarian', 'primary_doctor', 'created_at']
    list_filter = ['date', 'veterinarian', 'primary_doctor']
    search_fields = ['veterinarian__name', 'primary_doctor__email']
    date_hierarchy = 'date'

@admin.register(TreatmentResult)
class TreatmentResultAdmin(admin.ModelAdmin):
    list_display = ['feeding_observation', 'treatment_doctor', 'result_type', 'follow_up_days', 'created_at']
    list_filter = ['result_type', 'created_at', 'treatment_doctor']
    search_fields = ['feeding_observation__cow__cow_number', 'diagnosis', 'treatment_content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'feeding_observation__cow', 'treatment_doctor'
        ) 