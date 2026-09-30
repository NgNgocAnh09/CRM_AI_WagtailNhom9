from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from home.models import CRMDashboardPage, Customer, Order, Resource, Note


class CRMDashboardPageTests(WagtailPageTestCase):
    """
    Tests for CRMDashboardPage creation and rendering.
    """

    def setUp(self):
        root_page = Page.get_first_root_node()
        Site.objects.create(hostname="testsite", root_page=root_page, is_default_site=True)

        self.dashboard_page = CRMDashboardPage(
            title="Trang Quản Trị CRM AI",
            intro="<p>Chào mừng đến với hệ thống Smart CRM.</p>"
        )
        root_page.add_child(instance=self.dashboard_page)

    def test_dashboard_is_renderable(self):
        self.assertPageIsRenderable(self.dashboard_page)

    def test_dashboard_context(self):
        customer = Customer.objects.create(
            name="Nguyễn Văn Test",
            email="test@example.com",
            phone="0901234567",
            company="Công ty Test"
        )
        response = self.client.get(self.dashboard_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("customers", response.context)
        self.assertIn("total_customers", response.context)
        self.assertEqual(response.context["total_customers"], 1)


class CRMModelTests(TestCase):
    """
    Tests for CRM models (Customer, Order, Resource, Note).
    """

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Trần Thị B",
            email="tranthib@example.com",
            phone="0987654321",
            company="Công ty B"
        )

    def test_customer_str(self):
        self.assertEqual(str(self.customer), "Trần Thị B (tranthib@example.com)")

    def test_order_creation(self):
        order = Order.objects.create(
            customer=self.customer,
            order_number="ORD-TEST001",
            title="Gói CRM Basic",
            amount=5000000.00,
            status="completed"
        )
        self.assertEqual(str(order), "ORD-TEST001 - Gói CRM Basic (Trần Thị B)")

    def test_resource_creation(self):
        resource = Resource.objects.create(
            name="Phần mềm Wagtail CRM",
            category="software",
            price=12000000.00,
            quantity=5
        )
        self.assertEqual(str(resource), "Phần mềm Wagtail CRM [Phần mềm / License]")

    @patch('home.models.analyze_note_content')
    def test_note_ai_triggers_on_save(self, mock_analyze):
        mock_analyze.return_value = {
            "summary": "Khách hàng muốn mua gói CRM Enterprise.",
            "category": "Tiềm năng",
            "next_action": "Gửi báo giá và hợp đồng mẫu trong 24h."
        }

        note = Note.objects.create(
            customer=self.customer,
            content="Khách hàng quan tâm và hỏi giá gói CRM Enterprise."
        )

        mock_analyze.assert_called_once()
        self.assertEqual(note.ai_summary, "Khách hàng muốn mua gói CRM Enterprise.")
        self.assertEqual(note.ai_category, "Tiềm năng")
        self.assertEqual(note.ai_next_action, "Gửi báo giá và hợp đồng mẫu trong 24h.")


class CRMViewsTests(TestCase):
    """
    Tests for frontend interaction views.
    """

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Lê Văn C",
            email="levanc@example.com",
            phone="0912345678"
        )

    def test_add_customer_view(self):
        response = self.client.post(reverse('crm_add_customer'), {
            'name': 'Hoàng Văn D',
            'email': 'hoangvand@example.com',
            'phone': '0933445566',
            'company': 'Công ty D',
            'status': 'potential'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Customer.objects.filter(email='hoangvand@example.com').exists())

    @patch('home.models.analyze_note_content')
    def test_add_note_view(self, mock_analyze):
        mock_analyze.return_value = {
            "summary": "Ghi chú gọi điện hỏi thăm.",
            "category": "Đang cân nhắc",
            "next_action": "Gọi lại tư vấn tuần sau."
        }

        response = self.client.post(reverse('crm_add_note'), {
            'customer_id': self.customer.id,
            'content': 'Đã gọi điện trao đổi thông tin dịch vụ.'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.first()
        self.assertEqual(note.customer, self.customer)
        self.assertEqual(note.ai_category, "Đang cân nhắc")

    def test_add_order_view(self):
        response = self.client.post(reverse('crm_add_order'), {
            'customer_id': self.customer.id,
            'title': 'Dịch vụ tư vấn CRM',
            'amount': '3000000',
            'status': 'completed'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.title, 'Dịch vụ tư vấn CRM')
        self.assertEqual(order.amount, 3000000)

    def test_add_resource_view(self):
        response = self.client.post(reverse('crm_add_resource'), {
            'name': 'Gói Bảo trì 1 năm',
            'category': 'service',
            'price': '2000000',
            'quantity': '10',
            'description': 'Dịch vụ bảo trì phần mềm'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resource.objects.count(), 1)
        res = Resource.objects.first()
        self.assertEqual(res.name, 'Gói Bảo trì 1 năm')
