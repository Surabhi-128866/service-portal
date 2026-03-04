from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Doctor, Patient, Appointment, Prescription, Leave

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'fee', 'is_active', 'user')
    search_fields = ('name', 'specialization')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time_slot', 'status')
    list_filter = ('status', 'date')
    actions = ['cancel_appointments']

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'Cancelled':
            self.send_cancellation_email(obj)
        super().save_model(request, obj, form, change)

    @admin.action(description='Cancel selected appointments and notify patients')
    def cancel_appointments(self, request, queryset):
        for appt in queryset:
            if appt.status != 'Cancelled':
                appt.status = 'Cancelled'
                appt.save()
                self.send_cancellation_email(appt)
        self.message_user(request, "Selected appointments cancelled and emails sent.")

    def send_cancellation_email(self, appointment):
        subject = 'Appointment Cancelled - MediCare'
        message = f"Dear {appointment.patient.user.username},\n\nYour appointment with Dr. {appointment.doctor.name} on {appointment.date} at {appointment.time_slot} has been cancelled by the administration.\n\nSorry for the inconvenience.\n\nRegards,\nMediCare Team"
        patient_email = appointment.patient.user.email
        if patient_email:
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [patient_email])
            except Exception as e:
                print(f"Failed to send email: {e}")

admin.site.register(Prescription)
admin.site.register(Leave)
