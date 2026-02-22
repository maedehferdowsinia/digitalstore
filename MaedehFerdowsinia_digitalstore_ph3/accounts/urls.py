from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView
app_name = 'accounts'
urlpatterns = [
    path('signup/seller/', views.seller_signup, name='seller_signup'),
    path('signup/buyer/', views.buyer_signup, name='buyer_signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # logout
    # ⭐ فاز ۴ – تایید ایمیل
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
]
