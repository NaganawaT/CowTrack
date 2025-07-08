from django import forms
from django.utils import timezone
from .models import Cow, Veterinarian, Treatment, FeedingObservation, Medicine, TreatmentMedicine, DailyVeterinarian, TreatmentResult

class ExcelUploadForm(forms.Form):
    """Excelファイルアップロード用フォーム"""
    excel_file = forms.FileField(
        label='Excelファイル',
        help_text='牛のデータが含まれたExcelファイルを選択してください（.xlsx, .xls）',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    
    # オプション設定
    skip_duplicates = forms.BooleanField(
        label='重複データをスキップ',
        required=False,
        initial=True,
        help_text='既に登録されている個体識別番号のデータはスキップします',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    update_existing = forms.BooleanField(
        label='既存データを更新',
        required=False,
        initial=False,
        help_text='既に登録されている個体識別番号のデータを更新します',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    skip_check_digit = forms.BooleanField(
        label='チェックデジット検証をスキップ',
        required=False,
        initial=False,
        help_text='個体識別番号のチェックデジット検証をスキップします（推奨しません）',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class CowForm(forms.ModelForm):
    """牛登録・編集用フォーム"""
    
    class Meta:
        model = Cow
        fields = ['cow_number', 'shed_code', 'intake_date', 'gender', 'origin_region', 'status']
        widgets = {
            'cow_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10桁の個体識別番号を入力'
            }),
            'shed_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '4桁の牛舎番号を入力'
            }),
            'intake_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'origin_region': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'cow_number': '牛個体識別番号（10桁）',
            'shed_code': '牛舎番号',
            'intake_date': '導入日',
            'gender': '性別',
            'origin_region': '導入元地域',
            'status': 'ステータス'
        }

class TreatmentForm(forms.ModelForm):
    """治療履歴登録・編集用フォーム"""
    
    # 薬剤の複数選択フィールド
    medicines = forms.ModelMultipleChoiceField(
        queryset=Medicine.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'medicine-checkbox'
        }),
        required=False,
        label='投薬'
    )
    
    # 薬剤ごとの投与日数フィールド
    medicine_dosage_days = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        label='投与日数'
    )
    
    class Meta:
        model = Treatment
        fields = ['cow', 'veterinarian', 'primary_doctor', 'treatment_date', 'diagnosis', 'treatment_content', 'treatment_type', 'note']
        widgets = {
            'cow': forms.Select(attrs={
                'class': 'form-control'
            }),
            'veterinarian': forms.Select(attrs={
                'class': 'form-control'
            }),
            'primary_doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'treatment_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '診断内容を入力してください'
            }),
            'treatment_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '治療内容を入力してください'
            }),
            'treatment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'その他の備考を入力してください'
            })
        }
        labels = {
            'cow': '対象牛',
            'veterinarian': '獣医師',
            'primary_doctor': '主治療担当者',
            'treatment_date': '治療日時',
            'diagnosis': '診断',
            'treatment_content': '治療内容',
            'treatment_type': '治療種別',
            'note': '備考'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 活動中の牛のみを選択肢に表示し、下5桁の牛番号を数値順で並び替え
        cows = Cow.objects.filter(status='active')
        cows_list = list(cows)
        cows_list.sort(key=lambda cow: int(cow.cow_number[-5:]) if cow.cow_number.isdigit() and len(cow.cow_number) >= 5 else float('inf'))
        
        # ソートされた選択肢を設定
        choices = [('', '牛を選択してください')] + [(cow.id, f"{cow.shed_code}｜{cow.intake_date.month if cow.intake_date else '-'}｜{cow.origin_region[:1]}｜{cow.cow_number[-5:]}") for cow in cows_list]
        self.fields['cow'].choices = choices
        
        # 有効な獣医師のみを選択肢に表示
        veterinarians = Veterinarian.objects.filter(is_active=True).order_by('name')
        vet_choices = [('', '獣医師を選択してください')] + [(vet.id, f"{vet.name} ({vet.license_number})" if vet.license_number else vet.name) for vet in veterinarians]
        self.fields['veterinarian'].choices = vet_choices
        
        # 治療担当者（User）のみを選択肢に表示
        from django.contrib.auth import get_user_model
        User = get_user_model()
        doctors = User.objects.filter(role='治療担当', is_active=True).order_by('email')
        doctor_choices = [('', '主治療担当者を選択してください（任意）')] + [(user.id, user.email) for user in doctors]
        self.fields['primary_doctor'].choices = doctor_choices
        
        # 新規作成時のみ、治療日時を現在の時間に設定
        if not self.instance.pk:  # 新規作成の場合
            now = timezone.now()
            # datetime-local形式に変換（YYYY-MM-DDTHH:MM）
            formatted_now = now.strftime('%Y-%m-%dT%H:%M')
            self.fields['treatment_date'].initial = formatted_now
        
        # 編集時は既存の薬剤を選択状態にする
        if self.instance.pk:
            existing_medicines = self.instance.get_medicines()
            self.fields['medicines'].initial = [tm.medicine for tm in existing_medicines]
    
    def save(self, commit=True):
        treatment = super().save(commit=False)
        
        if commit:
            treatment.save()
            
            # 既存の薬剤関連を削除
            treatment.treatmentmedicine_set.all().delete()
            
            # 新しい薬剤関連を作成
            medicines = self.cleaned_data.get('medicines', [])
            medicine_dosage_days = self.cleaned_data.get('medicine_dosage_days', '')
            
            if medicines and medicine_dosage_days:
                try:
                    dosage_data = eval(medicine_dosage_days)  # JSON文字列を辞書に変換
                    for medicine in medicines:
                        dosage_days = dosage_data.get(str(medicine.id), medicine.default_days or 1)
                        TreatmentMedicine.objects.create(
                            treatment=treatment,
                            medicine=medicine,
                            dosage_days=dosage_days
                        )
                except:
                    # エラーが発生した場合はデフォルト値を使用
                    for medicine in medicines:
                        TreatmentMedicine.objects.create(
                            treatment=treatment,
                            medicine=medicine,
                            dosage_days=medicine.default_days or 1
                        )
        
        return treatment

class FeedingObservationForm(forms.ModelForm):
    """餌観察記録登録・編集用フォーム"""
    
    class Meta:
        model = FeedingObservation
        fields = ['cow', 'observed_at', 'appetite', 'symptoms', 'memo']
        widgets = {
            'cow': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observed_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'appetite': forms.Select(attrs={
                'class': 'form-control'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '症状や異常を入力してください'
            }),
            'memo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'その他の観察事項を入力してください'
            })
        }
        labels = {
            'cow': '対象牛',
            'observed_at': '観察日時',
            'appetite': '食欲',
            'symptoms': '症状・異常',
            'memo': '備考'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 活動中の牛のみを選択肢に表示し、下5桁の牛番号を数値順で並び替え
        cows = Cow.objects.filter(status='active')
        cows_list = list(cows)
        cows_list.sort(key=lambda cow: int(cow.cow_number[-5:]) if cow.cow_number.isdigit() and len(cow.cow_number) >= 5 else float('inf'))
        
        # ソートされた選択肢を設定
        choices = [('', '牛を選択してください')] + [(cow.id, f"{cow.shed_code}｜{cow.intake_date.month if cow.intake_date else '-'}｜{cow.origin_region[:1]}｜{cow.cow_number[-5:]}") for cow in cows_list]
        self.fields['cow'].choices = choices
        
        # 新規作成時のみ、観察日時を現在の時間に設定
        if not self.instance.pk:  # 新規作成の場合
            now = timezone.now()
            # datetime-local形式に変換（YYYY-MM-DDTHH:MM）
            formatted_now = now.strftime('%Y-%m-%dT%H:%M')
            self.fields['observed_at'].initial = formatted_now 

class VeterinarianForm(forms.ModelForm):
    """獣医師マスタ登録・編集用フォーム"""
    
    class Meta:
        model = Veterinarian
        fields = ['name', 'license_number', 'phone', 'email', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '獣医師名を入力'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '獣医師免許番号を入力（任意）'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '電話番号を入力'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'メールアドレスを入力'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': '獣医師名',
            'license_number': '獣医師免許番号（任意）',
            'phone': '電話番号',
            'email': 'メールアドレス',
            'is_active': '有効'
        }

class DailyVeterinarianForm(forms.ModelForm):
    """日別獣医師設定登録・編集用フォーム"""
    
    class Meta:
        model = DailyVeterinarian
        fields = ['date', 'veterinarian', 'primary_doctor']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'veterinarian': forms.Select(attrs={
                'class': 'form-control'
            }),
            'primary_doctor': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'date': '日付',
            'veterinarian': '獣医師',
            'primary_doctor': '主治療担当者'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 有効な獣医師のみを選択肢に表示
        veterinarians = Veterinarian.objects.filter(is_active=True).order_by('name')
        vet_choices = [('', '獣医師を選択してください')] + [(vet.id, f"{vet.name} ({vet.license_number})" if vet.license_number else vet.name) for vet in veterinarians]
        self.fields['veterinarian'].choices = vet_choices
        
        # 治療担当者（User）のみを選択肢に表示
        from django.contrib.auth import get_user_model
        User = get_user_model()
        doctors = User.objects.filter(role='治療担当', is_active=True).order_by('email')
        doctor_choices = [('', '主治療担当者を選択してください（任意）')] + [(user.id, user.email) for user in doctors]
        self.fields['primary_doctor'].choices = doctor_choices
        
        # 新規作成時のみ、日付を今日に設定
        if not self.instance.pk:  # 新規作成の場合
            today = timezone.now().date()
            self.fields['date'].initial = today 

class TreatmentResultForm(forms.ModelForm):
    """治療結果登録・編集用フォーム"""
    
    class Meta:
        model = TreatmentResult
        fields = ['result_type', 'follow_up_days', 'diagnosis', 'treatment_content', 'note']
        widgets = {
            'result_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'follow_up_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30',
                'placeholder': '経過観察日数を入力'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '診断内容を入力'
            }),
            'treatment_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '治療内容を入力'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '備考を入力'
            }),
        }
        labels = {
            'result_type': '治療結果',
            'follow_up_days': '経過観察日数',
            'diagnosis': '診断内容',
            'treatment_content': '治療内容',
            'note': '備考'
        } 