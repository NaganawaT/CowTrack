from django.urls import path
from . import views

app_name = 'cattle'

urlpatterns = [
    # モバイル版専用（一時的に無効化）
    # path('mobile/', views.MobileDashboardView.as_view(), name='mobile_dashboard'),
    # path('mobile/cows/', views.MobileCowListView.as_view(), name='mobile_cow_list'),
    # path('mobile/treatments/', views.MobileTreatmentListView.as_view(), name='mobile_treatment_list'),
    # path('mobile/treatments/create/', views.MobileTreatmentCreateView.as_view(), name='mobile_treatment_create'),
    # path('mobile/feeding-observations/', views.MobileFeedingObservationListView.as_view(), name='mobile_feeding_observation_list'),
    # path('mobile/feeding-observations/create/', views.MobileFeedingObservationCreateView.as_view(), name='mobile_feeding_observation_create'),
    # path('mobile/feeding-observations/<int:pk>/edit/', views.MobileFeedingObservationUpdateView.as_view(), name='mobile_feeding_observation_edit'),
    
    # ダッシュボード
    path('', views.dashboard, name='dashboard'),
    
    # テストページ
    path('test-hamburger/', views.test_hamburger_view, name='test_hamburger'),
    
    # 牛管理
    path('cows/', views.cow_list, name='cow_list'),
    path('cows/add/', views.cow_form, name='cow_form'),
    path('cows/<int:pk>/', views.cow_detail, name='cow_detail'),
    path('cows/<int:pk>/edit/', views.cow_form, name='cow_edit'),
    path('cows/<int:pk>/delete/', views.CowDeleteView.as_view(), name='cow_confirm_delete'),
    
    # 治療履歴管理
    path('treatments/', views.treatment_list, name='treatment_list'),
    path('treatments/add/', views.treatment_form, name='treatment_form'),
    path('treatments/<int:pk>/', views.treatment_detail, name='treatment_detail'),
    path('treatments/<int:pk>/edit/', views.treatment_form, name='treatment_edit'),
    path('treatments/<int:pk>/delete/', views.TreatmentDeleteView.as_view(), name='treatment_confirm_delete'),
    
    # 餌観察記録管理
    path('feeding-observations/', views.feeding_observation_list, name='feeding_observation_list'),
    path('feeding-observations/add/', views.feeding_observation_form, name='feeding_observation_form'),
    path('feeding-observations/<int:pk>/', views.feeding_observation_detail, name='feeding_observation_detail'),
    path('feeding-observations/<int:pk>/edit/', views.feeding_observation_form, name='feeding_observation_edit'),
    path('feeding-observations/<int:pk>/delete/', views.FeedingObservationDeleteView.as_view(), name='feeding_observation_confirm_delete'),
    
    # 治療一覧・治療結果管理
    path('treatment-summary/', views.treatment_summary_list, name='treatment_summary_list'),
    path('treatment-result/<int:observation_id>/create/', views.TreatmentResultCreateView.as_view(), name='treatment_result_create'),
    
    # 日別獣医師設定管理
    path('daily-veterinarians/', views.daily_veterinarian_list, name='daily_veterinarian_list'),
    path('daily-veterinarians/add/', views.daily_veterinarian_form, name='daily_veterinarian_form'),
    path('daily-veterinarians/<int:pk>/edit/', views.DailyVeterinarianUpdateView.as_view(), name='daily_veterinarian_edit'),
    path('daily-veterinarians/<int:pk>/delete/', views.DailyVeterinarianDeleteView.as_view(), name='daily_veterinarian_confirm_delete'),
    
    # API endpoints
    path('api/cows-by-shed/', views.get_cows_by_shed, name='get_cows_by_shed'),
    path('api/cows-from-feeding-observations/', views.get_cows_from_feeding_observations, name='get_cows_from_feeding_observations'),
    path('api/cow/<int:cow_id>/latest-treatment/', views.get_latest_treatment, name='get_latest_treatment'),
    path('api/shed-subcategories/', views.get_shed_subcategories, name='get_shed_subcategories'),
    path('api/sheds-by-subcategory/', views.get_sheds_by_subcategory, name='get_shed_by_subcategory'),
    
    # カスタム管理画面
    path('admin/login/', views.custom_admin_login, name='custom_admin_login'),
    path('admin/dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/cows/', views.custom_admin_cows, name='custom_admin_cows'),
    path('admin/treatments/', views.custom_admin_treatments, name='custom_admin_treatments'),
    
    path('feeding-observations/add/', views.feeding_observation_form, name='feeding_observation_form'),
    path('feeding-observations/<int:pk>/', views.feeding_observation_detail, name='feeding_observation_detail'),
    path('feeding-observations/<int:pk>/edit/', views.feeding_observation_form, name='feeding_observation_edit'),
    path('feeding-observations/<int:pk>/delete/', views.feeding_observation_confirm_delete, name='feeding_observation_confirm_delete'),
    
    path('treatments/add/', views.treatment_form, name='treatment_form'),
    path('treatments/<int:pk>/', views.treatment_detail, name='treatment_detail'),
    path('treatments/<int:pk>/edit/', views.treatment_form, name='treatment_edit'),
    path('treatments/<int:pk>/delete/', views.treatment_confirm_delete, name='treatment_confirm_delete'),
    
    path('treatment-results/', views.treatment_result_form, name='treatment_result_form'),
    path('daily-veterinarians/add/', views.daily_veterinarian_form, name='daily_veterinarian_form'),
] 