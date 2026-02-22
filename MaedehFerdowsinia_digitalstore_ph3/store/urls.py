from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),

    path('files/', views.file_list, name='file_list'),
    path('files/<int:pk>/', views.file_detail, name='file_detail'),

    path('upload/', views.upload_file, name='upload_file'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:file_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('buyer-dashboard/',views.buyer_dashboard,name='buyer_dashboard'),

]
