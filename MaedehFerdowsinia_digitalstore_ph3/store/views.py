from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, FileResponse, Http404
from django.db.models import Count, Sum
from .models import OrderItem

from .models import File, Order, OrderItem
from .forms import FileUploadForm

import logging
logger = logging.getLogger('store')


# -------------------------
# صفحه اصلی
# -------------------------
@login_required
def home(request):
    logger.info(f"User {request.user.username} accessed home page")
    files = File.objects.all()

    purchased_files = OrderItem.objects.filter(
        order__buyer=request.user,
        order__is_paid=True
    ).values_list('file', flat=True)

    #context = {
     #   'files': files,
      #  'purchased_files': purchased_files
    #}
    return render(request, 'store/file_list.html', {
        'files': files,
        'purchased_files': purchased_files
    })


# -------------------------
# لیست فایل‌ها
# -------------------------
@login_required
def file_list(request):
    user = request.user

    if user.is_seller:
        # فروشنده فقط فایل‌های خودش
        files = File.objects.filter(seller=user)
        purchased_files = File.objects.none()
    else:
        # خریدار همه فایل‌ها را می‌بیند
        files = File.objects.available()

        purchased_files = File.objects.purchased_by(request.user)

    return render(request, 'store/file_list.html', {
        'files': files,
        'purchased_files': purchased_files
    })


# -------------------------
# جزئیات فایل
# -------------------------
@login_required
def file_detail(request, pk):
    file = get_object_or_404(File, pk=pk)

    already_purchased = OrderItem.objects.filter(
        order__buyer=request.user,
        order__is_paid=True,
        file=file
    ).exists()

    return render(request, 'store/file_detail.html', {
        'file': file,
        'already_purchased': already_purchased
    })


# -------------------------
# آپلود فایل (فقط فروشنده)
# -------------------------
@login_required
def upload_file(request):
    if not request.user.is_seller:
        logger.warning(
            f"Unauthorized upload attempt by user {request.user.username}"
        )
        return HttpResponseForbidden("Only sellers can upload files")

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.seller = request.user
            file.save()

            logger.info(
                f"File {file.id} uploaded by seller {request.user.username}"
            )

            return redirect('store:file_list')
    else:
        form = FileUploadForm()

    return render(request, 'store/upload_file.html', {'form': form})


# -------------------------
# داشبورد فروشنده
# -------------------------
@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        return HttpResponseForbidden("Access denied")

    files = File.objects.by_seller(request.user)

    total_income = OrderItem.objects.filter(
        file__seller=request.user
    ).aggregate(
        income=Sum('file__price')
    )['income'] or 0

    return render(request, 'store/seller_dashboard.html', {
        'files': files,
        'total_income': total_income
    })


# -------------------------
# داشبورد خریدار
# -------------------------
@login_required
def buyer_dashboard(request):
    purchased_items = OrderItem.objects.purchased_by(request.user)

    return render(request, 'store/buyer_dashboard.html', {
        'purchased_items': purchased_items
    })




# -------------------------
# افزودن به سبد خرید
# -------------------------
@login_required
def add_to_cart(request, file_id):
    cart = request.session.get('cart', [])
    if file_id not in cart:
        cart.append(file_id)
        logger.info(
            f"User {request.user.username} added file {file_id} to cart"
        )
    request.session['cart'] = cart
    return redirect('store:cart')



# -------------------------
# مشاهده سبد خرید
# -------------------------
@login_required
def cart_view(request):
    cart = request.session.get('cart', [])
    files = File.objects.filter(id__in=cart)
    total_price = sum(file.price for file in files)

    return render(request, 'store/cart.html', {
        'files': files,
        'total_price': total_price
    })


# -------------------------
# پرداخت
# -------------------------
@login_required
def checkout(request):
    cart = request.session.get('cart', [])
    files = File.objects.filter(id__in=cart)

    if not files.exists():
        return redirect('store:file_list')

    # فقط فایل‌هایی که قبلاً نخریده
    purchased_file_ids = OrderItem.objects.filter(
        order__buyer=request.user,
        order__is_paid=True
    ).values_list('file_id', flat=True)

    files_to_buy = files.exclude(id__in=purchased_file_ids)

    if not files_to_buy.exists():
        return redirect('store:file_list')

    order = Order.objects.create(
        buyer=request.user,
        is_paid=True
    )

    for file in files_to_buy:
        OrderItem.objects.create(order=order, file=file)

    request.session['cart'] = []
    return redirect('store:buyer_dashboard')


# -------------------------
# دانلود فایل (بعد از خرید)
# -------------------------
@login_required
def download_file(request, file_id):
    has_access = OrderItem.objects.filter(
        order__buyer=request.user,
        order__is_paid=True,
        file_id=file_id
    ).exists()

    if not has_access:
        return HttpResponseForbidden("شما این فایل را نخریده‌اید")

    file_obj = get_object_or_404(File, id=file_id)

    return FileResponse(
        file_obj.file.open(),
        as_attachment=True,
        filename=file_obj.file.name
    )
