from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

# 1. Model Khách hàng (Được đăng ký Snippet để quản lý riêng)
@register_snippet
class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên khách hàng")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    company = models.CharField(max_length=255, blank=True, null=True, verbose_name="Công ty")

    panels = [
        FieldPanel('name'),
        FieldPanel('email'),
        FieldPanel('phone'),
        FieldPanel('company'),
    ]

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"


# 2. Model Ghi chú (Được đăng ký Snippet)
@register_snippet
class Note(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes', verbose_name="Khách hàng")
    content = RichTextField(verbose_name="Nội dung ghi chú")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    panels = [
        FieldPanel('customer'),
        FieldPanel('content'),
    ]

    def __str__(self):
        return f"Ghi chú cho {self.customer.name} - {self.created_at.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Ghi chú"
        verbose_name_plural = "Ghi chú"


# 3. CRMDashboardPage (Trang hiển thị trên Wagtail CMS)
class CRMDashboardPage(Page):
    intro = RichTextField(blank=True, verbose_name="Giới thiệu Dashboard")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = []  # Không cho tạo trang con nếu không cần thiết
    max_count = 1       # Chỉ cho phép tạo 1 trang Dashboard duy nhất trong hệ thống

    class Meta:
        verbose_name = "Trang Quản Trị CRM"