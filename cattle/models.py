from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.

# カスタムユーザーモデルを一時的に無効化
# class User(AbstractUser):
#     """ユーザーモデル"""
#     ROLE_CHOICES = [
#         ('餌担当', '餌担当'),
#         ('治療担当', '治療担当'),
#         ('事務', '事務'),
#         ('管理者', '管理者'),
#     ]
#     
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES)
#     email = models.EmailField(unique=True)
#     
#     def __str__(self):
#         return self.email
#     
#     def get_full_name(self):
#         return self.username
#     
#     def get_short_name(self):
#         return self.username

class Veterinarian(models.Model):
    """獣医師マスタ"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='獣医師名')
    license_number = models.CharField(max_length=20, unique=True, verbose_name='獣医師免許番号', blank=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話番号')
    email = models.EmailField(blank=True, verbose_name='メールアドレス')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.license_number})" if self.license_number else self.name
    
    class Meta:
        verbose_name = '獣医師'
        verbose_name_plural = '獣医師'
        ordering = ['name']

class Cow(models.Model):
    """牛の基本情報"""
    STATUS_CHOICES = [
        ('active', '活動中'),
        ('inactive', '非活動'),
    ]
    
    GENDER_CHOICES = [
        ('castrated', '去勢'),
        ('female', 'メス'),
    ]
    
    ORIGIN_REGION_CHOICES = [
        ('北海道', '北海道'),
        ('曽於', '曽於'),
        ('関', '関'),
        ('飛騨', '飛騨'),
        ('自家', '自家'),
    ]
    
    id = models.AutoField(primary_key=True)
    cow_number = models.CharField(max_length=20, unique=True, verbose_name='牛番号')
    shed_code = models.CharField(max_length=10, verbose_name='牛舎番号')
    intake_date = models.DateField(null=True, blank=True, verbose_name='導入日')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')
    origin_region = models.CharField(max_length=50, null=True, blank=True, verbose_name='導入元地域')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='ステータス')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cow_number
    
    class Meta:
        verbose_name = '牛'
        verbose_name_plural = '牛'

class Medicine(models.Model):
    """薬剤情報"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='薬剤名')
    description = models.TextField(blank=True, verbose_name='説明')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '薬剤'
        verbose_name_plural = '薬剤'

class Treatment(models.Model):
    """治療履歴"""
    TREATMENT_TYPE_CHOICES = [
        ('initial', '初回治療'),
        ('follow_up', '経過観察'),
        ('emergency', '緊急治療'),
    ]
    
    id = models.AutoField(primary_key=True)
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE, verbose_name='対象牛')
    veterinarian = models.ForeignKey(Veterinarian, on_delete=models.CASCADE, verbose_name='獣医師', null=True, blank=True)
    primary_doctor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='主治療担当者', null=True, blank=True)
    treatment_date = models.DateTimeField(verbose_name='治療日時')
    diagnosis = models.CharField(max_length=255, verbose_name='診断')
    treatment_content = models.TextField(verbose_name='治療内容')
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_TYPE_CHOICES, default='initial', verbose_name='治療種別')
    note = models.TextField(blank=True, verbose_name='備考')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.cow.cow_number} - {self.treatment_date}"
    
    def get_medicines(self):
        """この治療で使用された薬剤を取得"""
        return TreatmentMedicine.objects.filter(treatment=self)
    
    class Meta:
        verbose_name = '治療履歴'
        verbose_name_plural = '治療履歴'

class TreatmentMedicine(models.Model):
    """治療-薬剤関連"""
    id = models.AutoField(primary_key=True)
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, verbose_name='治療履歴')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, verbose_name='薬剤')
    dosage_days = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], verbose_name='投薬日数')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.treatment.cow.cow_number} - {self.medicine.name}"
    
    class Meta:
        verbose_name = '治療薬剤'
        verbose_name_plural = '治療薬剤'

class DailyVeterinarian(models.Model):
    """日別獣医師設定"""
    id = models.AutoField(primary_key=True)
    date = models.DateField(unique=True, verbose_name='日付')
    veterinarian = models.ForeignKey(Veterinarian, on_delete=models.CASCADE, verbose_name='獣医師')
    primary_doctor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='主治療担当者', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.date} - {self.veterinarian.name}"
    
    class Meta:
        verbose_name = '日別獣医師設定'
        verbose_name_plural = '日別獣医師設定'
        ordering = ['-date']

class FeedingObservation(models.Model):
    """餌観察記録"""
    APPETITE_CHOICES = [
        ('○', '○'),
        ('△', '△'),
        ('×', '×'),
        ('-', '-'),
    ]
    
    TREATMENT_STATUS_CHOICES = [
        ('untreated', '未治療'),
        ('re_examination', '再診'),
        ('self_treatment', '自己治療'),
        ('follow_up', '経過観察'),
    ]
    
    id = models.AutoField(primary_key=True)
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    observer = models.ForeignKey(User, on_delete=models.CASCADE)
    observed_at = models.DateTimeField()
    appetite = models.CharField(max_length=1, choices=APPETITE_CHOICES, null=True, blank=True)
    symptoms = models.CharField(max_length=255, null=True, blank=True)
    memo = models.CharField(max_length=255, null=True, blank=True)
    treatment_status = models.CharField(max_length=20, choices=TREATMENT_STATUS_CHOICES, default='untreated', verbose_name='治療状況')
    
    def __str__(self):
        return f"{self.cow.cow_number} - {self.observed_at}"
    
    class Meta:
        verbose_name = '餌観察記録'
        verbose_name_plural = '餌観察記録'

class TreatmentResult(models.Model):
    """治療結果"""
    RESULT_TYPE_CHOICES = [
        ('re_examination', '再診'),
        ('self_treatment', '自己治療'),
        ('follow_up', '経過観察'),
    ]
    
    id = models.AutoField(primary_key=True)
    feeding_observation = models.ForeignKey(FeedingObservation, on_delete=models.CASCADE, verbose_name='餌観察記録')
    treatment_doctor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='治療担当者')
    result_type = models.CharField(max_length=20, choices=RESULT_TYPE_CHOICES, verbose_name='治療結果')
    follow_up_days = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)], null=True, blank=True, verbose_name='経過観察日数')
    diagnosis = models.TextField(blank=True, verbose_name='診断内容')
    treatment_content = models.TextField(blank=True, verbose_name='治療内容')
    note = models.TextField(blank=True, verbose_name='備考')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.feeding_observation.cow.cow_number} - {self.get_result_type_display()}"
    
    class Meta:
        verbose_name = '治療結果'
        verbose_name_plural = '治療結果'
        ordering = ['-created_at']

class MovementLog(models.Model):
    """移動履歴"""
    id = models.AutoField(primary_key=True)
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    from_shed_code = models.CharField(max_length=4, null=True, blank=True)
    to_shed_code = models.CharField(max_length=4)
    moved_at = models.DateField()
    moved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.cow.cow_number} {self.from_shed_code}→{self.to_shed_code}"

class FollowUpObservation(models.Model):
    """経過観察"""
    APPETITE_CHOICES = [
        ('○', '○'),
        ('△', '△'),
        ('×', '×'),
        ('-', '-'),
    ]
    
    id = models.AutoField(primary_key=True)
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    observed_at = models.DateTimeField()
    observer = models.ForeignKey(User, on_delete=models.CASCADE)
    appetite = models.CharField(max_length=1, choices=APPETITE_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return f"{self.treatment.cow.cow_number} - {self.observed_at}"
    
    class Meta:
        verbose_name = '経過観察'
        verbose_name_plural = '経過観察'