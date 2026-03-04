from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from hospital.models import Appointment

class Command(BaseCommand):
    help = 'Send morning email alerts to patients with appointments today.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        # Get all confirmed appointments for today
        appointments = Appointment.objects.filter(date=today, status='Confirmed')
        
        count = 0
        for appt in appointments:
            patient_email = appt.patient.user.email
            if patient_email:
                subject = f"Appointment Alert - Today at {appt.time_slot}"
                message = f"Dear {appt.patient.user.username},\n\nThis is a friendly reminder that you have an appointment today with Dr. {appt.doctor.name} at {appt.time_slot}.\n\nPlease arrive 10 minutes prior to your time block.\n\nRegards,\nMediCare Team"
                
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [patient_email])
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"Sent email to {patient_email} for appointment {appt.id}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send email to {patient_email}: {e}"))
                    
        self.stdout.write(self.style.SUCCESS(f'Successfully sent {count} morning alerts.'))
