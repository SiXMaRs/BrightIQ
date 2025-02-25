from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    path('menu/', menu_view, name='menu'),
    path('add-to-cart/<int:menu_id>/', add_to_cart_view, name='add_to_cart'),
    path('cart/', cart_view, name='cart'),
    path('update-cart/<int:cart_id>/', update_cart_view, name='update_cart'),
    path('order/', order_view, name='order'),

    path('list-menu/', add_menu_view, name='list_menu'),
    path('edit-menu/', edit_menu_view, name='edit_menu'),
    path('delete-menu/<int:menu_id>/', delete_menu_view, name='delete_menu'),
    path('order-history/', order_history_view, name='order_history'),
    path('create-order-from-store/', create_order_from_store, name='create_order_from_store'),
]
