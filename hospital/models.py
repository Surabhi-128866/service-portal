from django.db import models
from accounts.models import CustomUser

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    experience = models.CharField(max_length=100)
    specialization = models.CharField(max_length=255)
    about_description = models.TextField()
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)
    license_no = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user.user_type not in [1, 2]:
            self.user.user_type = 2
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.user.user_type not in [1, 2]:
            self.user.user_type = 3
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )

    ATTENDANCE_CHOICES = (
        ('Pending', 'Pending'),
        ('Attended', 'Attended'),
        ('Missed', 'Missed'),
    )

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=50) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    attendance = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='Pending')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username} with {self.doctor.name} on {self.date}"

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    details = models.TextField()
    date_prescribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment}"

class Leave(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Leave for {self.doctor.name} from {self.start_date} to {self.end_date}"
