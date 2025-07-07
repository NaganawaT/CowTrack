from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta, time, datetime
from .models import Cow, Veterinarian, Treatment, FeedingObservation, DailyVeterinarian, TreatmentResult
from .forms import CowForm, TreatmentForm, FeedingObservationForm, DailyVeterinarianForm, TreatmentResultForm, ExcelUploadForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .utils import get_shed_groups, get_shed_hierarchy, get_shed_hierarchy_combined, process_excel_file
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

def test_hamburger_view(request):
    """ハンバーガーメニューテスト用ビュー"""
    return render(request, 'cattle/test_hamburger.html')

class DashboardView(TemplateView):
    """ダッシュボード画面"""
    template_name = 'cattle/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 統計情報
        context['total_cows'] = Cow.objects.count()
        context['active_cows'] = Cow.objects.filter(status='active').count()
        context['inactive_cows'] = Cow.objects.filter(status='inactive').count()
        
        # 治療履歴統計
        today = timezone.now().date()
        context['today_treatments'] = Treatment.objects.filter(
            treatment_date__date=today
        ).count()
        context['week_treatments'] = Treatment.objects.filter(
            treatment_date__gte=today - timedelta(days=7)
        ).count()
        context['month_treatments'] = Treatment.objects.filter(
            treatment_date__gte=today - timedelta(days=30)
        ).count()
        
        # 最近の治療履歴
        context['recent_treatments'] = Treatment.objects.select_related('cow').order_by(
            '-treatment_date'
        )[:5]
        
        # 最近登録された牛
        context['recent_cows'] = Cow.objects.order_by('-id')[:5]
        
        # 牛舎別統計
        context['shed_stats'] = Cow.objects.filter(status='active').values('shed_code').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return context

class CowListView(ListView):
    model = Cow
    template_name = 'cattle/cow_list.html'
    context_object_name = 'cows'
    paginate_by = 20

    def get_queryset(self):
        queryset = Cow.objects.all().order_by('-id')
        
        # 検索機能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cow_number__icontains=search) |
                Q(shed_code__icontains=search)
            )
        
        # ステータスフィルター
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(status='active')
        elif status == 'inactive':
            queryset = queryset.exclude(status='active')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 統計情報
        context['total_cows'] = Cow.objects.count()
        context['active_cows'] = Cow.objects.filter(status='active').count()
        context['recent_treatments'] = Treatment.objects.filter(
            treatment_date__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return context

class CowDetailView(DetailView):
    model = Cow
    template_name = 'cattle/cow_detail.html'
    context_object_name = 'cow'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 治療履歴を取得
        context['treatments'] = self.object.treatment_set.all().order_by('-treatment_date')
        return context

class CowCreateView(CreateView):
    model = Cow
    form_class = CowForm
    template_name = 'cattle/cow_form.html'
    success_url = reverse_lazy('cattle:cow_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '新しい牛を登録'
        context['submit_text'] = '登録'
        return context

    def form_valid(self, form):
        messages.success(self.request, '牛の登録が完了しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class CowUpdateView(UpdateView):
    model = Cow
    form_class = CowForm
    template_name = 'cattle/cow_form.html'
    success_url = reverse_lazy('cattle:cow_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.cow_number} の編集'
        context['submit_text'] = '更新'
        return context

    def form_valid(self, form):
        messages.success(self.request, '牛の情報を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

# 治療履歴管理ビュー
class TreatmentListView(ListView):
    model = Treatment
    template_name = 'cattle/treatment_list.html'
    context_object_name = 'treatments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Treatment.objects.select_related('cow').all().order_by('-treatment_date')
        
        # 検索機能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cow__cow_number__icontains=search) |
                Q(diagnosis__icontains=search) |
                Q(note__icontains=search)
            )
        
        # 牛番号フィルター
        cow_id = self.request.GET.get('cow')
        if cow_id:
            queryset = queryset.filter(cow_id=cow_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 統計情報
        context['total_treatments'] = Treatment.objects.count()
        context['recent_treatments'] = Treatment.objects.filter(
            treatment_date__gte=timezone.now() - timedelta(days=7)
        ).count()
        context['cows'] = Cow.objects.filter(status='active').order_by('cow_number')
        
        return context

class TreatmentDetailView(DetailView):
    model = Treatment
    template_name = 'cattle/treatment_detail.html'
    context_object_name = 'treatment'

class TreatmentCreateView(CreateView):
    model = Treatment
    form_class = TreatmentForm
    template_name = 'cattle/treatment_form.html'
    success_url = reverse_lazy('cattle:treatment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '新しい治療履歴を登録'
        context['submit_text'] = '登録'
        
        # 事前選択された牛がある場合
        cow_id = self.request.GET.get('cow')
        if cow_id:
            try:
                cow = Cow.objects.get(id=cow_id)
                context['preselected_cow'] = cow
            except Cow.DoesNotExist:
                pass
        
        return context

    def form_valid(self, form):
        # 日別獣医師設定がある場合は、その獣医師を設定
        treatment_date = form.cleaned_data['treatment_date']
        daily_vet = DailyVeterinarian.objects.filter(date=treatment_date.date()).first()
        
        if daily_vet and not form.cleaned_data.get('veterinarian'):
            form.instance.veterinarian = daily_vet.veterinarian
            form.instance.primary_doctor = daily_vet.primary_doctor
        
        messages.success(self.request, '治療履歴を登録しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class TreatmentUpdateView(UpdateView):
    model = Treatment
    form_class = TreatmentForm
    template_name = 'cattle/treatment_form.html'
    success_url = reverse_lazy('cattle:treatment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '治療履歴を編集'
        context['submit_text'] = '更新'
        
        # 日別獣医師設定を取得
        today = timezone.now().date()
        try:
            daily_vet = DailyVeterinarian.objects.get(date=today)
            context['daily_veterinarian'] = daily_vet.veterinarian
        except DailyVeterinarian.DoesNotExist:
            context['daily_veterinarian'] = None
        
        return context

    def form_valid(self, form):
        # 日別獣医師設定がある場合は、その獣医師を設定
        today = timezone.now().date()
        try:
            daily_vet = DailyVeterinarian.objects.get(date=today)
            form.instance.doctor = daily_vet.veterinarian
        except DailyVeterinarian.DoesNotExist:
            pass  # 日別設定がない場合は既存の獣医師を維持
        
        messages.success(self.request, '治療履歴を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

# 餌観察記録管理ビュー
class FeedingObservationListView(ListView):
    model = FeedingObservation
    template_name = 'cattle/feeding_observation_list.html'
    context_object_name = 'observations'
    paginate_by = 20

    def get_queryset(self):
        queryset = FeedingObservation.objects.select_related('cow').prefetch_related('cow__treatment_set').all()
        sort = self.request.GET.get('sort', 'normal')
        
        # 日付フィルター
        date_filter = self.request.GET.get('date')
        if date_filter:
            try:
                from datetime import datetime
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(observed_at__date=filter_date)
            except ValueError:
                # 日付が無効な場合は今日の日付を使用
                queryset = queryset.filter(observed_at__date=timezone.now().date())
        else:
            # 日付が指定されていない場合は今日の日付を使用
            queryset = queryset.filter(observed_at__date=timezone.now().date())
        
        # 検索機能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cow__cow_number__icontains=search) |
                Q(symptoms__icontains=search) |
                Q(memo__icontains=search)
            )
        
        # 牛番号フィルター
        cow_id = self.request.GET.get('cow')
        if cow_id:
            queryset = queryset.filter(cow_id=cow_id)
        
        # 食欲フィルター
        appetite = self.request.GET.get('appetite')
        if appetite:
            queryset = queryset.filter(appetite=appetite)
        
        if sort == 'alternate':
            # 交互ソート: 先頭2桁ごとにグループ化し、交互に並べる
            cows = Cow.objects.filter(status='active').order_by('shed_code', 'cow_number')
            shed_codes = sorted(set(cow.shed_code for cow in cows))
            shed_prefixes = sorted(set(str(code)[:2] for code in shed_codes))
            shed_groups = {prefix: [code for code in shed_codes if str(code).startswith(prefix)] for prefix in shed_prefixes}
            # 交互順のshed_codeリストを作成
            max_len = max(len(lst) for lst in shed_groups.values())
            interleaved = []
            for i in range(max_len):
                for prefix in shed_prefixes:
                    if i < len(shed_groups[prefix]):
                        interleaved.append(shed_groups[prefix][i])
            # shed_code順で牛IDリストを作成
            cow_ids = []
            for shed_code in interleaved:
                cow_ids.extend(list(cows.filter(shed_code=shed_code).values_list('id', flat=True)))
            # cow_id順で観察記録を並べ替え
            obs = list(queryset)
            obs.sort(key=lambda o: (cow_ids.index(o.cow.id) if o.cow.id in cow_ids else 99999, -o.observed_at.timestamp()))
            return obs
        else:
            # 通常の牛舎番号昇順
            return queryset.order_by('cow__shed_code', 'cow__cow_number', '-observed_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 現在の日付を取得
        date_filter = self.request.GET.get('date')
        if date_filter:
            try:
                from datetime import datetime
                current_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            except ValueError:
                current_date = timezone.now().date()
        else:
            current_date = timezone.now().date()
        
        context['current_date'] = current_date
        context['current_date_str'] = current_date.strftime('%Y年%m月%d日')
        
        # 前日・翌日の日付を計算
        from datetime import timedelta
        context['prev_date'] = current_date - timedelta(days=1)
        context['next_date'] = current_date + timedelta(days=1)
        
        # 今日の日付かどうかを判定
        context['is_today'] = current_date == timezone.now().date()
        
        context['total_observations'] = FeedingObservation.objects.count()
        context['today_observations'] = FeedingObservation.objects.filter(
            observed_at__date=current_date
        ).count()
        
        # 下5桁の牛番号を数値順で並び替え
        cows = Cow.objects.filter(status='active')
        cows_list = list(cows)
        cows_list.sort(key=lambda cow: int(cow.cow_number[-5:]) if cow.cow_number.isdigit() and len(cow.cow_number) >= 5 else float('inf'))
        context['cows'] = cows_list
        
        # 新規登録の牛を判定（指定日付に登録された餌観察記録の牛で、治療状況が未治療または未設定のもの）
        new_observation_cows = set(
            FeedingObservation.objects.filter(
                observed_at__date=current_date
            ).filter(
                Q(treatment_status='untreated') | Q(treatment_status__isnull=True)
            ).values_list('cow_id', flat=True)
        )
        context['new_observation_cows'] = new_observation_cows
        
        # 並び順をテンプレートに渡す
        context['sort'] = self.request.GET.get('sort', 'normal')
        return context

class FeedingObservationDetailView(DetailView):
    model = FeedingObservation
    template_name = 'cattle/feeding_observation_detail.html'
    context_object_name = 'observation'

class FeedingObservationCreateView(CreateView):
    model = FeedingObservation
    form_class = FeedingObservationForm
    template_name = 'cattle/feeding_observation_form.html'

    def get_success_url(self):
        # 作成した餌観察記録の日付を取得
        observation_date = self.object.observed_at.date()
        # その日付の餌観察記録一覧ページにリダイレクト
        return reverse('cattle:feeding_observation_list') + f'?date={observation_date.strftime("%Y-%m-%d")}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '新しい餌観察記録を登録'
        context['submit_text'] = '登録'
        # 2段階プルダウン用の階層データ
        context['shed_hierarchy'] = get_shed_hierarchy()
        return context

    def form_valid(self, form):
        # 現在のユーザーを観察者として設定
        form.instance.observer = self.request.user
        messages.success(self.request, '餌観察記録を登録しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class FeedingObservationUpdateView(UpdateView):
    model = FeedingObservation
    form_class = FeedingObservationForm
    template_name = 'cattle/feeding_observation_form.html'

    def get_success_url(self):
        # 編集対象の餌観察記録の日付を取得
        observation_date = self.object.observed_at.date()
        # その日付の餌観察記録一覧ページにリダイレクト
        return reverse('cattle:feeding_observation_list') + f'?date={observation_date.strftime("%Y-%m-%d")}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '餌観察記録を編集'
        context['submit_text'] = '更新'
        # 2段階プルダウン用の階層データ
        context['shed_hierarchy'] = get_shed_hierarchy()
        
        # 編集時の対象牛の情報を追加
        if self.object and self.object.cow:
            cow = self.object.cow
            try:
                # origin_regionは文字列フィールドなので直接アクセス
                region_short = cow.origin_region if cow.origin_region else ''
                intake_month = cow.intake_date.strftime('%m') if cow.intake_date else ''
                display_name = f"{cow.shed_code}｜{intake_month}{region_short}｜{cow.cow_number[-5:]}"
            except Exception as e:
                # エラーが発生した場合は簡易的な表示名を使用
                display_name = f"{cow.shed_code}｜{cow.cow_number}"
            
            context['edit_cow_info'] = {
                'id': cow.id,
                'cow_number': cow.cow_number,
                'shed_code': cow.shed_code,
                'display_name': display_name
            }
        
        return context

    def form_valid(self, form):
        messages.success(self.request, '餌観察記録を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class FeedingObservationDeleteView(DeleteView):
    model = FeedingObservation
    template_name = 'cattle/feeding_observation_confirm_delete.html'

    def get_success_url(self):
        # 削除対象の餌観察記録の日付を取得
        observation_date = self.object.observed_at.date()
        # その日付の餌観察記録一覧ページにリダイレクト
        return reverse('cattle:feeding_observation_list') + f'?date={observation_date.strftime("%Y-%m-%d")}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '餌観察記録を削除'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, '餌観察記録を削除しました。')
        return super().delete(request, *args, **kwargs)

def cow_list(request):
    """牛一覧画面"""
    cows = Cow.objects.all()
    
    # 下5桁の牛番号を数値順で並び替え
    cows_list = list(cows)
    cows_list.sort(key=lambda cow: int(cow.cow_number[-5:]) if cow.cow_number.isdigit() and len(cow.cow_number) >= 5 else float('inf'))
    
    return render(request, 'cattle/cow_list.html', {
        'cows': cows_list
    })

def cow_detail(request, cow_id):
    """牛詳細画面"""
    cow = get_object_or_404(Cow, pk=cow_id)
    treatments = Treatment.objects.filter(cow=cow).order_by('-treatment_date')
    feeding_observations = FeedingObservation.objects.filter(cow=cow).order_by('-observed_at')
    
    return render(request, 'cattle/cow_detail.html', {
        'cow': cow,
        'treatments': treatments,
        'feeding_observations': feeding_observations
    })

def cow_create(request):
    """牛登録画面"""
    if request.method == 'POST':
        form = CowForm(request.POST)
        if form.is_valid():
            cow = form.save()
            messages.success(request, f'牛番号 {cow.cow_number} を登録しました。')
            return redirect('cattle:cow_detail', cow_id=cow.id)
    else:
        form = CowForm()
    
    return render(request, 'cattle/cow_form.html', {
        'form': form,
        'title': '新しい牛を登録',
        'submit_text': '登録'
    })

def get_cows_by_shed(request):
    """牛舎番号に基づいて牛の一覧を取得するAPI"""
    shed_code = request.GET.get('shed_code')
    if not shed_code:
        return JsonResponse({'error': '牛舎番号が指定されていません'}, status=400)
    
    try:
        cows = Cow.objects.filter(
            shed_code=shed_code,
            status='active'
        ).order_by('cow_number')
        
        # display_nameを含むデータを構築
        cows_data = []
        for cow in cows:
            try:
                # origin_regionは文字列フィールドなので直接アクセス
                region_short = cow.origin_region if cow.origin_region else ''
                intake_month = cow.intake_date.strftime('%m') if cow.intake_date else ''
                display_name = f"{cow.shed_code}｜{intake_month}{region_short}｜{cow.cow_number[-5:]}"
            except Exception as e:
                # エラーが発生した場合は簡易的な表示名を使用
                display_name = f"{cow.shed_code}｜{cow.cow_number}"
            
            cows_data.append({
                'id': cow.id,
                'cow_number': cow.cow_number,
                'shed_code': cow.shed_code,
                'display_name': display_name
            })
        
        return JsonResponse({
            'cows': cows_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_cows_from_feeding_observations(request):
    """餌観察記録から牛の一覧を取得するAPI"""
    try:
        # 餌観察記録に入っている牛を取得
        cows_with_observations = Cow.objects.filter(
            feedingobservation__isnull=False,
            status='active'
        ).distinct().values('id', 'cow_number', 'shed_code')
        
        # 下5桁の牛番号を数値順で並び替え
        cows_list = list(cows_with_observations)
        cows_list.sort(key=lambda cow: int(cow['cow_number'][-5:]) if cow['cow_number'].isdigit() and len(cow['cow_number']) >= 5 else float('inf'))
        
        return JsonResponse({
            'cows': cows_list
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def get_latest_treatment(request, cow_id):
    """指定された牛の過去最新の治療履歴を取得するAPI"""
    try:
        cow = get_object_or_404(Cow, id=cow_id)
        latest_treatment = Treatment.objects.filter(cow=cow).order_by('-treatment_date').first()
        
        if latest_treatment:
            # 薬剤情報を取得
            medicines = []
            for tm in latest_treatment.get_medicines():
                medicines.append({
                    'name': tm.medicine.name,
                    'dosage_days': tm.dosage_days
                })
            
            return JsonResponse({
                'treatment': True,
                'treatment_date': latest_treatment.treatment_date.strftime('%Y年%m月%d日 %H:%M'),
                'diagnosis': latest_treatment.diagnosis,
                'treatment_content': latest_treatment.treatment_content,
                'medicines': medicines,
                'note': latest_treatment.note
            })
        else:
            return JsonResponse({
                'treatment': False
            })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def get_shed_subcategories(request):
    """牛舎分類に基づいてサブカテゴリを取得するAPI"""
    category = request.GET.get('category')
    if not category:
        return JsonResponse({'subcategories': []})
    
    hierarchy = get_shed_hierarchy()
    
    if category == '導入牛舎':
        subcategories = list(hierarchy['導入牛舎'].keys())
    elif category == '肥育牛舎':
        subcategories = list(hierarchy['肥育牛舎'].keys())
    else:  # その他
        subcategories = []
    
    return JsonResponse({'subcategories': subcategories})

def get_sheds_by_subcategory(request):
    """サブカテゴリに基づいて牛舎番号を取得するAPI"""
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')
    
    if not category or not subcategory:
        return JsonResponse({'sheds': []})
    
    hierarchy = get_shed_hierarchy()
    
    if category == '導入牛舎' and subcategory in hierarchy['導入牛舎']:
        sheds = hierarchy['導入牛舎'][subcategory]
    elif category == '肥育牛舎' and subcategory in hierarchy['肥育牛舎']:
        sheds = hierarchy['肥育牛舎'][subcategory]
    else:
        sheds = []
    
    return JsonResponse({'sheds': sheds})

class MobileDashboardView(TemplateView):
    """モバイル版ダッシュボード画面"""
    template_name = 'cattle/mobile/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 統計情報
        context['total_cows'] = Cow.objects.count()
        context['active_cows'] = Cow.objects.filter(status='active').count()
        context['inactive_cows'] = Cow.objects.filter(status='inactive').count()
        
        # 治療履歴統計
        today = timezone.now().date()
        context['today_treatments'] = Treatment.objects.filter(
            treatment_date__date=today
        ).count()
        context['week_treatments'] = Treatment.objects.filter(
            treatment_date__gte=today - timedelta(days=7)
        ).count()
        context['month_treatments'] = Treatment.objects.filter(
            treatment_date__gte=today - timedelta(days=30)
        ).count()
        
        # 最近の治療履歴
        context['recent_treatments'] = Treatment.objects.select_related('cow').order_by(
            '-treatment_date'
        )[:5]
        
        # 最近登録された牛
        context['recent_cows'] = Cow.objects.order_by('-id')[:5]
        
        return context

class MobileCowListView(ListView):
    """モバイル版牛一覧画面"""
    model = Cow
    template_name = 'cattle/mobile/cow_list.html'
    context_object_name = 'cows'
    paginate_by = 20

    def get_queryset(self):
        queryset = Cow.objects.all().order_by('-id')
        
        # 検索機能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cow_number__icontains=search) |
                Q(shed_code__icontains=search)
            )
        
        # ステータスフィルター
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(status='active')
        elif status == 'inactive':
            queryset = queryset.exclude(status='active')
        
        return queryset

class MobileTreatmentListView(ListView):
    """モバイル版治療履歴一覧画面"""
    model = Treatment
    template_name = 'cattle/mobile/treatment_list.html'
    context_object_name = 'treatments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Treatment.objects.select_related('cow', 'doctor').order_by('-treatment_date')
        
        # 検索機能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cow__cow_number__icontains=search) |
                Q(diagnosis__icontains=search) |
                Q(note__icontains=search)
            )
        
        return queryset

class MobileFeedingObservationListView(ListView):
    """モバイル版餌観察記録一覧画面"""
    model = FeedingObservation
    template_name = 'cattle/mobile/feeding_observation_list.html'
    context_object_name = 'observations'
    paginate_by = 20

    def get_queryset(self):
        queryset = FeedingObservation.objects.select_related('cow', 'observer').order_by('-observed_at')
        
        # 検索機能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cow__cow_number__icontains=search) |
                Q(symptoms__icontains=search) |
                Q(memo__icontains=search)
            )
        
        return queryset

class MobileFeedingObservationCreateView(CreateView):
    """モバイル版餌観察記録作成画面"""
    model = FeedingObservation
    form_class = FeedingObservationForm
    template_name = 'cattle/mobile/feeding_observation_form.html'
    success_url = reverse_lazy('cattle:mobile_feeding_observation_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '餌観察記録登録'
        context['submit_text'] = '登録'
        context['shed_hierarchy'] = get_shed_hierarchy()
        return context
    
    def form_valid(self, form):
        form.instance.observer = self.request.user
        return super().form_valid(form)

class MobileFeedingObservationUpdateView(UpdateView):
    """モバイル版餌観察記録編集画面"""
    model = FeedingObservation
    form_class = FeedingObservationForm
    template_name = 'cattle/mobile/feeding_observation_form.html'
    success_url = reverse_lazy('cattle:mobile_feeding_observation_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '餌観察記録編集'
        context['submit_text'] = '更新'
        context['shed_hierarchy'] = get_shed_hierarchy()
        
        # 編集時の対象牛の情報を追加
        if self.object and self.object.cow:
            cow = self.object.cow
            try:
                # origin_regionは文字列フィールドなので直接アクセス
                region_short = cow.origin_region if cow.origin_region else ''
                intake_month = cow.intake_date.strftime('%m') if cow.intake_date else ''
                display_name = f"{cow.shed_code}｜{intake_month}{region_short}｜{cow.cow_number[-5:]}"
            except Exception as e:
                # エラーが発生した場合は簡易的な表示名を使用
                display_name = f"{cow.shed_code}｜{cow.cow_number}"
            
            context['edit_cow_info'] = {
                'id': cow.id,
                'cow_number': cow.cow_number,
                'shed_code': cow.shed_code,
                'display_name': display_name
            }
        
        return context
    
    def form_valid(self, form):
        return super().form_valid(form)

class MobileTreatmentCreateView(CreateView):
    """モバイル版治療履歴作成画面"""
    model = Treatment
    form_class = TreatmentForm
    template_name = 'cattle/mobile/treatment_form.html'
    success_url = reverse_lazy('cattle:mobile_treatment_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '治療履歴登録'
        context['submit_text'] = '登録'
        context['shed_hierarchy'] = get_shed_hierarchy()
        return context
    
    def form_valid(self, form):
        form.instance.doctor = self.request.user
        return super().form_valid(form)

# 日別獣医師設定管理ビュー
class DailyVeterinarianListView(ListView):
    """日別獣医師設定一覧画面"""
    model = DailyVeterinarian
    template_name = 'cattle/daily_veterinarian_list.html'
    context_object_name = 'daily_veterinarians'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '日別獣医師設定一覧'
        return context

class DailyVeterinarianCreateView(CreateView):
    """日別獣医師設定作成画面"""
    model = DailyVeterinarian
    form_class = DailyVeterinarianForm
    template_name = 'cattle/daily_veterinarian_form.html'
    success_url = reverse_lazy('cattle:daily_veterinarian_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '新しい日別獣医師設定を登録'
        context['submit_text'] = '登録'
        return context

    def form_valid(self, form):
        messages.success(self.request, '日別獣医師設定を登録しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class DailyVeterinarianUpdateView(UpdateView):
    """日別獣医師設定編集画面"""
    model = DailyVeterinarian
    form_class = DailyVeterinarianForm
    template_name = 'cattle/daily_veterinarian_form.html'
    success_url = reverse_lazy('cattle:daily_veterinarian_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.date} の日別獣医師設定を編集'
        context['submit_text'] = '更新'
        return context

    def form_valid(self, form):
        messages.success(self.request, '日別獣医師設定を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

class DailyVeterinarianDeleteView(DeleteView):
    """日別獣医師設定削除画面"""
    model = DailyVeterinarian
    template_name = 'cattle/daily_veterinarian_confirm_delete.html'
    success_url = reverse_lazy('cattle:daily_veterinarian_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '日別獣医師設定を削除'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, '日別獣医師設定を削除しました。')
        return super().delete(request, *args, **kwargs)

class TreatmentSummaryListView(ListView):
    """治療一覧ページ（治療担当者用）"""
    model = FeedingObservation
    template_name = 'cattle/treatment_summary_list.html'
    context_object_name = 'observations'
    paginate_by = 20

    def get_queryset(self):
        # 選択された日付または今日の餌観察記録を取得
        selected_date = self.request.GET.get('date')
        if selected_date:
            try:
                target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                target_date = timezone.now().date()
        else:
            target_date = timezone.now().date()
        
        # 表示フィルター（治療済みの表示/非表示）
        show_treated = self.request.GET.get('show_treated', 'true').lower() == 'true'
        
        if show_treated:
            # 治療済みも含めてすべて表示
            queryset = FeedingObservation.objects.select_related('cow').prefetch_related(
                'cow__treatment_set'
            ).filter(
                observed_at__date=target_date
            ).order_by('cow__shed_code', 'cow__cow_number')
        else:
            # 未治療のみ表示
            queryset = FeedingObservation.objects.select_related('cow').prefetch_related(
                'cow__treatment_set'
            ).filter(
                observed_at__date=target_date,
                treatment_status='untreated'
            ).order_by('cow__shed_code', 'cow__cow_number')
        
        # 検索機能
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cow__cow_number__icontains=search) |
                Q(symptoms__icontains=search) |
                Q(memo__icontains=search)
            )
        
        # 牛舎フィルター
        shed_code = self.request.GET.get('shed')
        if shed_code:
            queryset = queryset.filter(cow__shed_code=shed_code)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 選択された日付または今日の日付を取得
        selected_date = self.request.GET.get('date')
        if selected_date:
            try:
                current_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                current_date = timezone.now().date()
        else:
            current_date = timezone.now().date()
        
        # 前日・翌日の日付を計算
        prev_date = current_date - timedelta(days=1)
        next_date = current_date + timedelta(days=1)
        today = timezone.now().date()
        
        context['current_date'] = current_date
        context['current_date_str'] = current_date.strftime('%Y年%m月%d日')
        context['prev_date'] = prev_date
        context['next_date'] = next_date
        context['is_today'] = current_date == today
        
        # 表示フィルターの状態
        show_treated = self.request.GET.get('show_treated', 'true').lower() == 'true'
        context['show_treated'] = show_treated
        
        # 統計情報
        context['total_untreated'] = FeedingObservation.objects.filter(
            observed_at__date=current_date,
            treatment_status='untreated'
        ).count()
        
        context['total_treated'] = FeedingObservation.objects.filter(
            observed_at__date=current_date
        ).exclude(treatment_status='untreated').count()
        
        # 牛舎一覧
        context['sheds'] = Cow.objects.filter(status='active').values_list('shed_code', flat=True).distinct().order_by('shed_code')
        
        return context

class TreatmentResultCreateView(CreateView):
    """治療結果登録"""
    model = TreatmentResult
    form_class = TreatmentResultForm
    template_name = 'cattle/treatment_result_form.html'
    success_url = reverse_lazy('cattle:treatment_summary_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        observation_id = self.kwargs.get('observation_id')
        observation = get_object_or_404(FeedingObservation, id=observation_id)
        
        context['observation'] = observation
        context['title'] = f'{observation.cow.cow_number} の治療結果登録'
        context['submit_text'] = '登録'
        
        # 前回の治療履歴を取得（関連する薬剤情報も含める）
        latest_treatment = Treatment.objects.select_related(
            'veterinarian', 'primary_doctor'
        ).prefetch_related(
            'treatmentmedicine_set__medicine'
        ).filter(
            cow=observation.cow
        ).order_by('-treatment_date').first()
        
        context['latest_treatment'] = latest_treatment
        
        return context

    def form_valid(self, form):
        observation_id = self.kwargs.get('observation_id')
        observation = get_object_or_404(FeedingObservation, id=observation_id)
        
        # 治療担当者を設定
        form.instance.treatment_doctor = self.request.user
        form.instance.feeding_observation = observation
        
        # 餌観察記録の治療状況を更新
        observation.treatment_status = form.instance.result_type
        observation.save()
        
        # 再診または自己治療の場合、翌日の餌観察記録を自動登録
        if form.instance.result_type in ['re_examination', 'self_treatment']:
            tomorrow = timezone.now().date() + timedelta(days=1)
            
            # 翌日の餌観察記録が既に存在するかチェック
            existing_observation = FeedingObservation.objects.filter(
                cow=observation.cow,
                observed_at__date=tomorrow
            ).first()
            
            if not existing_observation:
                # 翌日の餌観察記録を作成（餌喰いは未記入）
                FeedingObservation.objects.create(
                    cow=observation.cow,
                    observer=self.request.user,
                    observed_at=timezone.make_aware(datetime.combine(tomorrow, time(9, 0))),  # 朝9時
                    appetite=None,  # 未記入
                    symptoms=f"{form.instance.get_result_type_display()}のため自動登録 - {observation.symptoms or '症状なし'}",
                    memo=f"{form.instance.get_result_type_display()}のため自動登録",
                    treatment_status='untreated'
                )
                messages.success(self.request, f'治療結果を登録し、翌日の餌観察記録を自動登録しました。')
            else:
                messages.success(self.request, '治療結果を登録しました。')
        
        # 経過観察の場合、指定した日数分の餌観察記録を自動登録
        elif form.instance.result_type == 'follow_up' and form.instance.follow_up_days:
            follow_up_days = form.instance.follow_up_days
            created_count = 0
            
            for i in range(1, follow_up_days + 1):
                target_date = timezone.now().date() + timedelta(days=i)
                
                # その日の餌観察記録が既に存在するかチェック
                existing_observation = FeedingObservation.objects.filter(
                    cow=observation.cow,
                    observed_at__date=target_date
                ).first()
                
                if not existing_observation:
                    # 餌観察記録を作成（餌喰いは未記入）
                    FeedingObservation.objects.create(
                        cow=observation.cow,
                        observer=self.request.user,
                        observed_at=timezone.make_aware(datetime.combine(target_date, time(9, 0))),  # 朝9時
                        appetite=None,  # 未記入
                        symptoms=f"経過観察のため自動登録（{i}日目） - {observation.symptoms or '症状なし'}",
                        memo=f"経過観察のため自動登録（{follow_up_days}日間）",
                        treatment_status='follow_up'
                    )
                    created_count += 1
            
            if created_count > 0:
                messages.success(self.request, f'治療結果を登録し、{created_count}日分の経過観察記録を自動登録しました。')
            else:
                messages.success(self.request, '治療結果を登録しました。')
        else:
            messages.success(self.request, '治療結果を登録しました。')
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります。')
        return super().form_invalid(form)

@csrf_exempt
def custom_admin_login(request):
    """カスタム管理画面ログイン"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # デバッグ情報をログに出力
        print(f"Login attempt - Username: {username}")
        
        # ユーザーが存在しない場合は作成
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"Created new user: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        print(f"Authentication result - User: {user}")
        if user:
            print(f"User is_staff: {user.is_staff}")
            print(f"User is_active: {user.is_active}")
        
        if user is not None and user.is_staff:
            login(request, user)
            print(f"Login successful for user: {username}")
            return redirect('cattle:custom_admin_dashboard')
        else:
            print(f"Login failed for user: {username}")
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')
    
    return render(request, 'cattle/custom_admin_login.html')

@login_required(login_url='/admin/login/')
def custom_admin_dashboard(request):
    """カスタム管理ダッシュボード"""
    if not request.user.is_staff:
        return redirect('cattle:custom_admin_login')
    
    # 統計情報を取得
    total_cows = Cow.objects.count()
    total_treatments = Treatment.objects.count()
    total_observations = FeedingObservation.objects.count()
    
    context = {
        'total_cows': total_cows,
        'total_treatments': total_treatments,
        'total_observations': total_observations,
    }
    
    return render(request, 'cattle/custom_admin_dashboard.html', context)

@login_required(login_url='/admin/login/')
def custom_admin_cows(request):
    """牛の管理ページ"""
    if not request.user.is_staff:
        return redirect('cattle:custom_admin_login')
    
    cows = Cow.objects.all().order_by('shed_code', 'cow_number')
    return render(request, 'cattle/custom_admin_cows.html', {'cows': cows})

@login_required(login_url='/admin/login/')
def custom_admin_treatments(request):
    """治療の管理ページ"""
    if not request.user.is_staff:
        return redirect('cattle:custom_admin_login')
    
    treatments = Treatment.objects.all().order_by('-treatment_date')
    return render(request, 'cattle/custom_admin_treatments.html', {'treatments': treatments})

@login_required(login_url='/admin/login/')
def excel_upload(request):
    """Excelファイルアップロード処理"""
    if not request.user.is_staff:
        return redirect('cattle:custom_admin_login')
    
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            skip_duplicates = form.cleaned_data['skip_duplicates']
            update_existing = form.cleaned_data['update_existing']
            
            # Excelファイルを処理
            results = process_excel_file(excel_file, skip_duplicates, update_existing)
            
            # 結果をメッセージとして表示
            if results['created'] > 0:
                messages.success(request, f'{results["created"]}件の牛データを登録しました。')
            if results['updated'] > 0:
                messages.success(request, f'{results["updated"]}件の牛データを更新しました。')
            if results['skipped'] > 0:
                messages.info(request, f'{results["skipped"]}件のデータをスキップしました。')
            if results['errors']:
                for error in results['errors']:
                    messages.error(request, error)
            
            return redirect('cattle:excel_upload')
    else:
        form = ExcelUploadForm()
    
    return render(request, 'cattle/excel_upload.html', {'form': form})

@login_required(login_url='/admin/login/')
def excel_upload_preview(request):
    """Excelファイルのプレビュー表示"""
    if not request.user.is_staff:
        return redirect('cattle:custom_admin_login')
    
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            
            try:
                import pandas as pd
                
                # Excelファイルを読み込み
                if excel_file.name.endswith('.xlsx'):
                    df = pd.read_excel(excel_file, engine='openpyxl')
                elif excel_file.name.endswith('.xls'):
                    df = pd.read_excel(excel_file, engine='xlrd')
                else:
                    messages.error(request, 'サポートされていないファイル形式です。')
                    return redirect('cattle:excel_upload')
                
                # プレビューデータを準備
                preview_data = df.head(10).to_dict('records')  # 最初の10行
                columns = list(df.columns)
                
                context = {
                    'preview_data': preview_data,
                    'columns': columns,
                    'total_rows': len(df),
                    'form': form
                }
                
                return render(request, 'cattle/excel_upload_preview.html', context)
                
            except Exception as e:
                messages.error(request, f'ファイルの読み込みに失敗しました: {str(e)}')
                return redirect('cattle:excel_upload')
    else:
        form = ExcelUploadForm()
    
    return render(request, 'cattle/excel_upload.html', {'form': form})
