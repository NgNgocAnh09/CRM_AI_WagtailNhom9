from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.html import strip_tags
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from .ai_services import analyze_note_content


# 1. Model Khách hàng
class Customer(models.Model):
    STATUS_CHOICES = [
        ('new', 'Mới tiếp cận'),
        ('contacted', 'Đã liên hệ'),
        ('potential', 'Tiềm năng'),
        ('customer', 'Khách hàng chính thức'),
        ('lost', 'Đã mất / Hủy'),
    ]

    name = models.CharField(max_length=255, verbose_name="Tên khách hàng")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    company = models.CharField(max_length=255, blank=True, null=True, verbose_name="Công ty")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new', verbose_name="Trạng thái khách hàng")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    panels = [
        FieldPanel('name'),
        FieldPanel('email'),
        FieldPanel('phone'),
        FieldPanel('company'),
        FieldPanel('status'),
        FieldPanel('created_at'),
    ]

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"
        ordering = ['-created_at']


# 2. Model Đơn hàng
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name="Khách hàng")
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Mã đơn hàng")
    title = models.CharField(max_length=255, verbose_name="Tên đơn hàng / Dịch vụ")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá trị (VNĐ)")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái đơn hàng")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    panels = [
        FieldPanel('customer'),
        FieldPanel('order_number'),
        FieldPanel('title'),
        FieldPanel('amount'),
        FieldPanel('status'),
        FieldPanel('created_at'),
    ]

    def __str__(self):
        return f"{self.order_number} - {self.title} ({self.customer.name})"

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']


# 3. Model Tài nguyên doanh nghiệp / Sản phẩm & Dịch vụ
class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('product', 'Sản phẩm'),
        ('service', 'Dịch vụ CRM'),
        ('equipment', 'Thiết bị / Hạ tầng'),
        ('software', 'Phần mềm / License'),
    ]

    name = models.CharField(max_length=255, verbose_name="Tên tài nguyên / Sản phẩm")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='product', verbose_name="Loại tài nguyên")
    description = RichTextField(blank=True, verbose_name="Mô tả tài nguyên")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Đơn giá (VNĐ)")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng / Khả dụng")
    is_active = models.BooleanField(default=True, verbose_name="Đang kích hoạt")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    panels = [
        FieldPanel('name'),
        FieldPanel('category'),
        FieldPanel('description'),
        FieldPanel('price'),
        FieldPanel('quantity'),
        FieldPanel('is_active'),
        FieldPanel('created_at'),
    ]

    def __str__(self):
        return f"{self.name} [{self.get_category_display()}]"

    class Meta:
        verbose_name = "Tài nguyên doanh nghiệp"
        verbose_name_plural = "Tài nguyên doanh nghiệp"
        ordering = ['-created_at']


# 4. Model Ghi chú / Tương tác Khách hàng
class Note(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes', verbose_name="Khách hàng")
    content = RichTextField(verbose_name="Nội dung ghi chú")
    ai_summary = models.TextField(blank=True, null=True, verbose_name="AI Tóm tắt")
    ai_category = models.CharField(max_length=100, blank=True, null=True, verbose_name="AI Phân loại")
    ai_next_action = models.TextField(blank=True, null=True, verbose_name="AI Đề xuất hành động")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    panels = [
        FieldPanel('customer'),
        FieldPanel('content'),
        FieldPanel('ai_summary'),
        FieldPanel('ai_category'),
        FieldPanel('ai_next_action'),
        FieldPanel('created_at'),
    ]

    def save(self, *args, **kwargs):
        # Tự động gọi Gemini AI phân tích khi lưu ghi chú
        if self.content:
            plain_text = strip_tags(self.content)
            ai_result = analyze_note_content(plain_text)

            if ai_result.get("summary"):
                self.ai_summary = ai_result.get("summary")
            if ai_result.get("category"):
                self.ai_category = ai_result.get("category")
            if ai_result.get("next_action"):
                self.ai_next_action = ai_result.get("next_action")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ghi chú cho {self.customer.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Ghi chú & Tương tác"
        verbose_name_plural = "Ghi chú & Tương tác"
        ordering = ['-created_at']


# 5. Model CRMDashboardPage (Trang hiển thị Frontend trên Wagtail CMS)
class CRMDashboardPage(Page):
    intro = RichTextField(blank=True, verbose_name="Giới thiệu Dashboard CRM")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Lấy tham số tìm kiếm và bộ lọc từ request GET
        search_query = request.GET.get('q', '').strip()
        ai_category_filter = request.GET.get('ai_category', '').strip()
        status_filter = request.GET.get('status', '').strip()

        # Lấy danh sách khách hàng
        customers_qs = Customer.objects.all().prefetch_related('notes', 'orders')

        if search_query:
            customers_qs = customers_qs.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(company__icontains=search_query)
            )

        if status_filter:
            customers_qs = customers_qs.filter(status=status_filter)

        if ai_category_filter:
            customers_qs = customers_qs.filter(notes__ai_category__icontains=ai_category_filter).distinct()

        # Thống kê KPI tổng quan cho Dashboard
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        total_revenue_dict = Order.objects.filter(status='completed').aggregate(Sum('amount'))
        total_revenue = total_revenue_dict.get('amount__sum') or 0

        total_notes = Note.objects.count()
        total_resources = Resource.objects.count()

        # Phân bố AI Classification stats
        ai_stats = {
            'potential': Note.objects.filter(ai_category__icontains='Tiềm năng').count(),
            'considering': Note.objects.filter(ai_category__icontains='Đang cân nhắc').count(),
            'support': Note.objects.filter(ai_category__icontains='Khiếu nại').count() + Note.objects.filter(ai_category__icontains='Hỗ trợ').count(),
            'not_interested': Note.objects.filter(ai_category__icontains='Không quan tâm').count(),
        }

        # Danh sách đơn hàng & tài nguyên
        orders = Order.objects.select_related('customer').all()[:30]
        resources = Resource.objects.all()

        context.update({
            'customers': customers_qs,
            'orders': orders,
            'resources': resources,
            'search_query': search_query,
            'ai_category_filter': ai_category_filter,
            'status_filter': status_filter,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_notes': total_notes,
            'total_resources': total_resources,
            'ai_stats': ai_stats,
            'customer_status_choices': Customer.STATUS_CHOICES,
            'order_status_choices': Order.STATUS_CHOICES,
            'resource_category_choices': Resource.CATEGORY_CHOICES,
            'all_customers': Customer.objects.all(),
        })
        return context

    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Trang Quản Trị CRM"
