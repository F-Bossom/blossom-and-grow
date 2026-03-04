from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('plants/', views.plant_index, name='plant_index'),
    path('plants/<int:plant_id>/', views.plant_detail, name='plant_detail'),
    path('plants/create/', views.plant_create, name='plant_create'),
    path('plants/<int:plant_id>/edit/', views.plant_edit, name='plant_edit'),
    path('plants/<int:plant_id>/delete/', views.plant_delete, name='plant_delete'),
    path('plants/<int:plant_id>/care/add/', views.care_log_add, name='care_log_add'),
    path('care/<int:care_log_id>/delete/', views.care_log_delete, name='care_log_delete'),
    path('accounts/signup/', views.signup, name='signup'),
]