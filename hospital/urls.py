from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/add-prescription/<int:appointment_id>/', views.add_prescription, name='add_prescription'),
    path('doctor/mark-attendance/<int:appointment_id>/', views.mark_attendance, name='mark_attendance'),
    path('patient/book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('patient/confirm-payment/<int:appointment_id>/', views.confirm_payment, name='confirm_payment'),
]
