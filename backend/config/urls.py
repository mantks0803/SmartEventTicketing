from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/events/', include('events.urls')),
    path('api/seats/', include('seating.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/ai/', include('ai_agent.urls')),
]