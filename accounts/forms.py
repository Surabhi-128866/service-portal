from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from hospital.models import Patient

class PatientRegistrationForm(UserCreationForm):
    # Additional fields for patient profile
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 3  # Patient Role
        if commit:
            user.save()
            # Create associated patient profile
            Patient.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                address=self.cleaned_data.get('address')
            )
        return user
