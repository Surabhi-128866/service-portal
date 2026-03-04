from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import PatientRegistrationForm
from django.contrib.auth.forms import AuthenticationForm

def doctor_patient_login(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome {user.username}!")
                return redirect_user(user)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def patient_register(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('patient_dashboard')  # We will define this later
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def redirect_user(user):
    if user.user_type == 1 or user.is_superuser:
        return redirect('/admin/') # Send to django admin for now
    elif user.user_type == 2:
        return redirect('doctor_dashboard')
    elif user.user_type == 3:
        return redirect('patient_dashboard')
    return redirect('login')
