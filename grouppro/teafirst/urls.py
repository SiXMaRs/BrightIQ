from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    path('menu/', menu_view, name='menu'),
    path('cart/', cart_view, name='cart'),
    path('add_to_cart/<int:menu_id>/', add_to_cart, name='add_to_cart'),
    path('place_order/', place_order, name='place_order'),
    path('update_cart/<int:cart_id>/<str:action>/', update_cart_quantity, name='update_cart_quantity'),
    path('remove_from_cart/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),
    path('my-orders/', user_order_history_view, name='user_order'),

    path('list-menu/', add_menu_view, name='list_menu'),
    path('edit-menu/', edit_menu_view, name='edit_menu'),
    path('delete-menu/<int:menu_id>/', delete_menu_view, name='delete_menu'),
    path('order-history/', order_history_view, name='order_history'),
    path('create-order-from-store/', create_order_from_store, name='create_order_from_store'),

    path("dashboard/", dashboard, name="dashboard"),
]
