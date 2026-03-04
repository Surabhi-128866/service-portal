from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.doctor_patient_login, name='login'),
    path('register/', views.patient_register, name='patient_register'),
    path('logout/', views.custom_logout, name='logout'),
]
