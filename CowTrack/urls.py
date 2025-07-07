"""CowTrack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.conf.urls.static import static
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """ヘルスチェック用のエンドポイント"""
    try:
        logger.info(f"Health check accessed from {request.META.get('REMOTE_ADDR', 'unknown')}")
        return JsonResponse({"status": "OK", "message": "CowTrack is running"}, status=200)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JsonResponse({"status": "ERROR", "message": str(e)}, status=500)

urlpatterns = [
    path('', include('cattle.urls')),
    path('django-admin/', admin.site.urls),  # Django標準管理画面を別パスに移動
    path('health/', health_check, name='health_check'),
]

# 本番環境での静的ファイル配信
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
