from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('list/', views.transaction_list, name='transaction_list'),
    path('reports/', views.reports, name='reports'),
    path('api/reports-data/', views.reports_api, name='reports_api'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
]