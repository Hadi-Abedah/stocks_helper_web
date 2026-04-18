from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('stocks/<str:stock_symbol>/', views.stock_detail, name='stock_detail'),

]