from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('', lambda request: redirect('dashboard', permanent=False)),
]
