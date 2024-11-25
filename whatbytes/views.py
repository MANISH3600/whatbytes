from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, LoginForm

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logins')
    else:
        form = UserRegistrationForm()
    return render(request, 'whatbytes/register.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data["username_or_email"]
            password = form.cleaned_data["password"]
            user = User.objects.filter(email=username_or_email).first() if '@' in username_or_email else User.objects.filter(username=username_or_email).first()

            if user and user.check_password(password):
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()

    return render(request, "whatbytes/login.html", {"form": form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("logins")

@login_required
def dashboard(request):
    return render(request, "whatbytes/dashboard.html", {"user": request.user})

@login_required
def profile(request):
    return render(request, "whatbytes/profile.html", {"user": request.user})

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully.")
            return redirect("dashboard")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "whatbytes/change_password.html", {"form": form})

def send_test_email(request):
    try:
        send_mail(
            subject='Test Email Subject',
            message='This is a test email to verify email functionality.',
            from_email='guptamanish1006@gmail.com',
            recipient_list=['guptamanish1006360@gmail.com']
        )
        return HttpResponse("Test email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Error sending email: {str(e)}")


from .tasks import send_password_reset_email  # Import the Celery task
def password_reset_request(request):
    if request.method == "POST":
        print("Request received for password reset.")
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)  # Fetch the user directly
                print(f"User found: {user}")

                subject = "Password Reset Requested"
                email_content = (
                    f"Hello {user.username},\n\n"
                    f"Please click the link below to reset your password:\n\n"
                    f"http://{request.get_host()}/reset/{urlsafe_base64_encode(str(user.pk).encode())}/{default_token_generator.make_token(user)}\n\n"
                    "If you did not request a password reset, please ignore this email.\n\n"
                    "Thanks,\nWebsite Team"
                )
                send_password_reset_email.delay(subject, email_content, user.email)
                print(f"Password reset email sent to {user.email}")

                messages.success(request, "If this email is associated with an account, we have sent you a password reset email.")
                return redirect("logins")
            except User.DoesNotExist:
                print(f"No user found with email: {email}")
                messages.error(request, "No account found with that email address.")
    else:
        form = PasswordResetForm()

    return render(request, "whatbytes/password_reset.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect("logins")
        else:
            form = SetPasswordForm(user)
        return render(request, "whatbytes/password_reset_confirm.html", {"form": form})
    else:
        messages.error(request, "The reset link is invalid.")
        return redirect("password_reset")
