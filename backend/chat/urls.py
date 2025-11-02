from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_conversations),
    path('<int:conv_id>/', views.get_conversation),
    path('create/', views.create_conversation),
    path('<int:conv_id>/send/', views.send_message),
    path('<int:conv_id>/end/', views.end_conversation),
    path('dashboard/', views.dashboard_stats),
    path('status/', views.system_status),
    path('conversations/<int:conv_id>/end/', views.end_conversation),
 
]
