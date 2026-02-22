from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .forms import SellerSignUpForm, BuyerSignUpForm
from .models import User

app_name = 'accounts'


# ======================
# ثبت‌نام فروشنده
# ======================
def seller_signup(request):
    if request.method == 'POST':
        form = SellerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_seller = True
            user.is_buyer = False
            user.is_active = True
            user.is_email_verified = False
            user.save()

            send_verification_email(request, user)
            messages.success(request, 'ایمیل تایید برای شما ارسال شد.')

            return redirect('accounts:login')

    else:
        form = SellerSignUpForm()

    return render(request, 'accounts/seller_signup.html', {'form': form})


# ======================
# ثبت‌نام خریدار
# ======================
def buyer_signup(request):
    if request.method == 'POST':
        form = BuyerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_buyer = True
            user.is_seller = False
            user.is_active = True
            user.is_email_verified = False
            user.save()

            send_verification_email(request, user)
            messages.success(request, 'ایمیل تایید برای شما ارسال شد.')

            return redirect('accounts:login')

    else:
        form = BuyerSignUpForm()

    return render(request, 'accounts/buyer_signup.html', {'form': form})


# ======================
# ارسال ایمیل تایید
# ======================
def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_url = request.build_absolute_uri(
        reverse('accounts:verify_email', args=[uid, token])
    )

    subject = 'تایید ایمیل حساب کاربری'
    message = f'''
سلام {user.username}

برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:

{verify_url}
'''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


# ======================
# تایید ایمیل
# ======================
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(request, 'ایمیل شما با موفقیت تایید شد. حالا می‌توانید وارد شوید.')
        return redirect('accounts:login')


    messages.error(request, 'لینک تایید نامعتبر است.')
    return redirect('accounts:login')



# ======================
# لاگین
# ======================
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_email_verified:
            messages.error(self.request, 'ابتدا ایمیل خود را تایید کنید.')
            return redirect('accounts:login')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('store:file_list')
