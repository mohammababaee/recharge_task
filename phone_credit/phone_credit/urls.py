from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/credit/', include('credits.urls')),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/recharge/', include('recharges.urls')),
]