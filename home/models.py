from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from django.utils.html import strip_tags
from .ai_services import analyze_note_content

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
    ai_summary = models.TextField(blank=True, null=True, verbose_name="AI Tóm tắt")
    ai_category = models.CharField(max_length=100, blank=True, null=True, verbose_name="AI Phân loại")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    panels = [
        FieldPanel('customer'),
        FieldPanel('content'),
        FieldPanel('ai_summary'),
        FieldPanel('ai_category'),
    ]

    def save(self, *args, **kwargs):
        # Nếu có nội dung, loại bỏ thẻ HTML và nhờ AI phân tích
        if self.content:
            plain_text = strip_tags(self.content)
            ai_result = analyze_note_content(plain_text)
            
            # Chỉ ghi đè nếu AI trả về dữ liệu thành công
            if ai_result.get("summary"):
                self.ai_summary = ai_result.get("summary")
            if ai_result.get("category"):
                self.ai_category = ai_result.get("category")
                
        super().save(*args, **kwargs)

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