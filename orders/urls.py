from django.urls import path
from orders.views import (
    HoldSeatsView, CustomerOrderListView, OrderDetailView, 
    CancelOrderView, CreatePayOSPaymentView, PayOSWebhookView
)

urlpatterns = [
    path('hold/', HoldSeatsView.as_view(), name='hold_seats'),
    path('my-orders/', CustomerOrderListView.as_view(), name='customer_orders'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='cancel_order'),
    
    path('<int:order_id>/payos-link/', CreatePayOSPaymentView.as_view(), name='create_payos_link'),
    path('webhook/payos/', PayOSWebhookView.as_view(), name='payos_webhook'),
]