from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import Customer, Order, Resource, Note


class CustomerViewSet(SnippetViewSet):
    model = Customer
    icon = "user"
    menu_label = "Khách hàng"
    list_display = ["name", "email", "phone", "company", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "email", "phone", "company"]
    ordering = ["-created_at"]


class OrderViewSet(SnippetViewSet):
    model = Order
    icon = "shopping-cart"
    menu_label = "Đơn hàng"
    list_display = ["order_number", "title", "customer", "amount", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order_number", "title", "customer__name", "customer__email"]
    ordering = ["-created_at"]


class ResourceViewSet(SnippetViewSet):
    model = Resource
    icon = "box"
    menu_label = "Tài nguyên doanh nghiệp"
    list_display = ["name", "category", "price", "quantity", "is_active", "created_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering = ["-created_at"]


class NoteViewSet(SnippetViewSet):
    model = Note
    icon = "doc-full"
    menu_label = "Ghi chú & AI Insights"
    list_display = ["customer", "ai_category", "ai_summary", "created_at"]
    list_filter = ["ai_category", "created_at"]
    search_fields = ["customer__name", "content", "ai_summary", "ai_category"]
    ordering = ["-created_at"]


class CRMSnippetGroup(SnippetViewSetGroup):
    menu_label = "Quản lý CRM"
    menu_icon = "group"
    menu_order = 200
    items = (CustomerViewSet, OrderViewSet, ResourceViewSet, NoteViewSet)


register_snippet(CRMSnippetGroup)
