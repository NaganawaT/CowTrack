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
import logging

logger = logging.getLogger(__name__)

def redirect_to_cow_list(request):
    """トップページを牛一覧にリダイレクト"""
    return redirect('cattle:cow_list')

def mobile_redirect(request):
    """モバイル版へのリダイレクト（一時的に無効化）"""
    # 一時的にPC版にリダイレクト
    return redirect('cattle:cow_list')
    
    # 元のコード（コメントアウト）
    # user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    # if any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad']):
    #     return redirect('cattle:mobile_dashboard')
    # else:
    #     return redirect('cattle:cow_list')

def health_check(request):
    """ヘルスチェック用のエンドポイント"""
    try:
        logger.info(f"Health check accessed from {request.META.get('REMOTE_ADDR', 'unknown')}")
        return JsonResponse({"status": "OK", "message": "CowTrack is running"}, status=200)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JsonResponse({"status": "ERROR", "message": str(e)}, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', mobile_redirect, name='home'),
    path('', include('cattle.urls')),
]
