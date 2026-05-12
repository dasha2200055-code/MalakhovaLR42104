from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('charts/', views.charts_page, name='charts'),
    path('help/', views.help_page, name='help'),
    path('download/', views.download_csv, name='download'),
    path('api/data/', views.get_data, name='get_data'),
]