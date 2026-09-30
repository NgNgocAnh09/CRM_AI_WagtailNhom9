import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Customer, Order, Resource, Note


@require_POST
def add_note_view(request):
    """
    Tạo ghi chú mới cho khách hàng từ giao diện Frontend.
    Khi Note được tạo và gọi save(), Gemini AI sẽ tự động phân tích (Tóm tắt, Phân loại, Đề xuất hành động).
    """
    customer_id = request.POST.get('customer_id')
    content = request.POST.get('content', '').strip()

    if not customer_id or not content:
        messages.error(request, "Vui lòng chọn Khách hàng và nhập nội dung ghi chú!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        customer = Customer.objects.get(pk=customer_id)
        note = Note.objects.create(
            customer=customer,
            content=content
        )
        messages.success(request, f"Đã thêm ghi chú mới cho {customer.name}! AI đã tự động phân loại: [{note.ai_category}].")
    except Exception as e:
        messages.error(request, f"Lỗi khi thêm ghi chú: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def add_customer_view(request):
    """
    Tạo thông tin khách hàng mới từ Frontend.
    """
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    company = request.POST.get('company', '').strip()
    status = request.POST.get('status', 'new')

    if not name or not email or not phone:
        messages.error(request, "Vui lòng điền đầy đủ Tên, Email và Số điện thoại khách hàng!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if Customer.objects.filter(email=email).exists():
        messages.error(request, f"Email '{email}' đã tồn tại trong hệ thống!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        customer = Customer.objects.create(
            name=name,
            email=email,
            phone=phone,
            company=company,
            status=status
        )
        messages.success(request, f"Đã thêm thành công khách hàng: {customer.name} ({customer.email})!")
    except Exception as e:
        messages.error(request, f"Lỗi khi tạo khách hàng: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def add_order_view(request):
    """
    Tạo đơn hàng mới cho khách hàng từ Frontend.
    """
    customer_id = request.POST.get('customer_id')
    title = request.POST.get('title', '').strip()
    amount_raw = request.POST.get('amount', '0').strip()
    status = request.POST.get('status', 'pending')

    if not customer_id or not title:
        messages.error(request, "Vui lòng chọn Khách hàng và nhập Tên đơn hàng!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        amount = float(amount_raw)
        customer = Customer.objects.get(pk=customer_id)
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        order = Order.objects.create(
            customer=customer,
            order_number=order_number,
            title=title,
            amount=amount,
            status=status
        )
        messages.success(request, f"Đã tạo đơn hàng {order.order_number} ({order.title}) thành công!")
    except Exception as e:
        messages.error(request, f"Lỗi khi tạo đơn hàng: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def add_resource_view(request):
    """
    Tạo tài nguyên doanh nghiệp / sản phẩm dịch vụ mới từ Frontend.
    """
    name = request.POST.get('name', '').strip()
    category = request.POST.get('category', 'product')
    description = request.POST.get('description', '').strip()
    price_raw = request.POST.get('price', '0').strip()
    quantity_raw = request.POST.get('quantity', '1').strip()

    if not name:
        messages.error(request, "Vui lòng nhập Tên tài nguyên / Sản phẩm!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        price = float(price_raw)
        quantity = int(quantity_raw)

        resource = Resource.objects.create(
            name=name,
            category=category,
            description=description,
            price=price,
            quantity=quantity,
            is_active=True
        )
        messages.success(request, f"Đã thêm tài nguyên doanh nghiệp: {resource.name}!")
    except Exception as e:
        messages.error(request, f"Lỗi khi tạo tài nguyên: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
def reanalyze_note_view(request, note_id):
    """
    Gọi lại Gemini AI để phân tích lại một ghi chú cụ thể.
    """
    note = get_object_or_404(Note, pk=note_id)
    try:
        # Gọi save() để kích hoạt AI phân tích lại
        note.save()
        messages.success(request, f"Đã phân tích lại ghi chú thành công! Phân loại AI hiện tại: [{note.ai_category}]")
    except Exception as e:
        messages.error(request, f"Lỗi khi phân tích lại ghi chú: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))
