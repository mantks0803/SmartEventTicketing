from django.urls import path
from orders.views import HoldSeatsView, CustomerOrderListView, OrderDetailView, CancelOrderView

urlpatterns = [
    path('hold/', HoldSeatsView.as_view(), name='hold_seats'),
    path('my-orders/', CustomerOrderListView.as_view(), name='customer_orders'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='cancel_order'),
]