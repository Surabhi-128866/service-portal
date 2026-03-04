from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, Prescription, Doctor, Leave

from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def home(request):
    return render(request, 'home.html')

@login_required
def patient_dashboard(request):
    if request.user.user_type != 3:
        return redirect('home')
    
    query = request.GET.get('q')
    doctors = Doctor.objects.filter(is_active=True)
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) | Q(specialization__icontains=query)
        )
    
    try:
        patient = request.user.patient
        appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time_slot')
    except:
        appointments = []
        
    context = {
        'doctors': doctors,
        'appointments': appointments,
        'query': query
    }
    return render(request, 'hospital/patient_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    if request.user.user_type != 2:
        return redirect('home')
    try:
        doctor = request.user.doctor
        appointments = Appointment.objects.filter(doctor=doctor).order_by('date', 'time_slot')
        leaves = Leave.objects.filter(doctor=doctor).order_by('-start_date')
    except:
        appointments = []
        leaves = []
    return render(request, 'hospital/doctor_dashboard.html', {'appointments': appointments, 'leaves': leaves})

@login_required
def add_prescription(request, appointment_id):
    if request.user.user_type != 2:
        return redirect('home')
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
    
    if hasattr(appointment, 'prescription'):
        messages.info(request, "A prescription already exists for this appointment.")
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        details = request.POST.get('details')
        if details:
            Prescription.objects.create(appointment=appointment, details=details)
            appointment.status = 'Completed'
            appointment.save()
            messages.success(request, "Prescription added successfully.")
            return redirect('doctor_dashboard')
        else:
            messages.error(request, "Prescription details cannot be empty.")
    
    return render(request, 'hospital/add_prescription.html', {'appointment': appointment})

@login_required
def book_appointment(request, doctor_id):
    if request.user.user_type != 3:
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
    
    if request.method == 'POST':
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        
        if date and time_slot:
            # Check if doctor is on leave
            is_on_leave = Leave.objects.filter(
                doctor=doctor,
                start_date__lte=date,
                end_date__gte=date
            ).exists()

            if is_on_leave:
                messages.error(request, f"Dr. {doctor.name} is on leave on the selected date. Please choose another date.")
                return redirect('book_appointment', doctor_id=doctor.id)

            # Enforce max 4 slots per time slot
            existing_count = Appointment.objects.filter(
                doctor=doctor, 
                date=date, 
                time_slot=time_slot,
                status__in=['Pending', 'Confirmed', 'Completed']
            ).count()

            if existing_count >= 4:
                messages.error(request, "This time slot is fully booked (Max 4 slots allowed). Please choose another time.")
                return redirect('book_appointment', doctor_id=doctor.id)

            # Create a pending appointment
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=request.user.patient,
                date=date,
                time_slot=time_slot,
                status='Pending'
            )
            # Redirect to dummy payment page
            return redirect('confirm_payment', appointment_id=appointment.id)
        else:
            messages.error(request, "Please select both date and time slot.")
            
    leaves = Leave.objects.filter(doctor=doctor, end_date__gte=timezone.now().date())
    return render(request, 'hospital/book_appointment.html', {'doctor': doctor, 'leaves': leaves})

@login_required
def confirm_payment(request, appointment_id):
    if request.user.user_type != 3:
        return redirect('home')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient, status='Pending')
    
    if request.method == 'POST':
        # Simulate successful payment
        appointment.is_paid = True
        appointment.status = 'Confirmed'
        appointment.save()
        
        # Send confirmation email
        subject = 'Appointment Confirmation - MediCare'
        message = f"Dear {appointment.patient.user.username},\n\nYour appointment with Dr. {appointment.doctor.name} on {appointment.date} at {appointment.time_slot} is confirmed.\n\nThank you for choosing MediCare."
        patient_email = appointment.patient.user.email
        if patient_email:
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [patient_email])
            except Exception as e:
                print(f"Failed to send email: {e}")
                
        messages.success(request, "Payment successful! Your appointment is confirmed and an email has been sent.")
        return redirect('patient_dashboard')
        
    return render(request, 'hospital/confirm_payment.html', {'appointment': appointment})

@login_required
def mark_attendance(request, appointment_id):
    if request.user.user_type != 2:
        return redirect('home')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
    
    if request.method == 'POST':
        attendance_val = request.POST.get('attendance')
        if attendance_val in dict(Appointment.ATTENDANCE_CHOICES).keys():
            appointment.attendance = attendance_val
            appointment.save()
            messages.success(request, f"Attendance marked as {attendance_val}.")
        
    return redirect('doctor_dashboard')
