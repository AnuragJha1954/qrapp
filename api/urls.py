from django.urls import path
from .views import restaurant_menu, place_order

urlpatterns = [
    path('restaurants/<int:id>/menu/', restaurant_menu, name='restaurant-menu'),
    path('order/place/', place_order, name='place-order'),
]
