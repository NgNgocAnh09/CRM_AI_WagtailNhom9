from django.urls import path
from . import views

urlpatterns = [
    path('crm/add-note/', views.add_note_view, name='crm_add_note'),
    path('crm/add-customer/', views.add_customer_view, name='crm_add_customer'),
    path('crm/add-order/', views.add_order_view, name='crm_add_order'),
    path('crm/add-resource/', views.add_resource_view, name='crm_add_resource'),
    path('crm/reanalyze-note/<int:note_id>/', views.reanalyze_note_view, name='crm_reanalyze_note'),
]
