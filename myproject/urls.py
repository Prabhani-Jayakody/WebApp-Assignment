from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('', include('accounts.urls')),
]

