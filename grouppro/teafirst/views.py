from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import *

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('login') 
    else:
        form = RegisterForm()
    return render(request, 'user/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('menu')
    else:
        form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

#User
@login_required(login_url='/login/')
def menu_view(request):
    menus = Menu.objects.all()
    return render(request, 'user/menu.html', {'menus': menus})

@login_required(login_url='/login/')
def add_to_cart_view(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, menu=menu)

    if not created:
        cart_item.quantity += 1 
        cart_item.save()

    return redirect('cart')

@login_required(login_url='/login/')
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.menu.price * item.quantity for item in cart_items)
    
    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required(login_url='/login/')
def update_cart_view(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == "increase":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()  

    return redirect('cart')

@login_required(login_url='/login/')
def order_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items:
        return redirect('cart')
    
    for item in cart_items:
        Order.objects.create(
            user=request.user,
            menu=item.menu,
            quantity=item.quantity,
            total_price=item.menu.price * item.quantity,
            image=item.menu.image 
        )
    cart_items.delete()

    return redirect('menu')






#Admin
@login_required(login_url='/login/')
def add_menu_view(request):
    if not request.user.is_staff: 
        return redirect('menu')

    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list_menu')
    else:
        form = MenuForm()
    menus = Menu.objects.all()
    return render(request, 'admin/list_menu.html', {'form': form, 'menus': menus})

@login_required(login_url='/login/')
def edit_menu_view(request):
    if not request.user.is_staff:
        return redirect('menu')

    if request.method == 'POST':
        menu_id = request.POST.get('menu_id')
        menu = get_object_or_404(Menu, id=menu_id)
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('list_menu') 
    return redirect('list_menu')

@login_required(login_url='/login/')
def delete_menu_view(request, menu_id):
    if not request.user.is_staff:
        return redirect('menu')

    menu = get_object_or_404(Menu, id=menu_id)
    if request.method == 'POST':
        menu.delete()
        return redirect('list_menu') 

    return redirect('list_menu')

@login_required(login_url='/login/')
def order_history_view(request):
    if not request.user.is_staff:
        return redirect('menu')

    orders = Order.objects.all()  

    if request.method == 'POST':
        order_id = request.POST.get('order_id')  
        order = get_object_or_404(Order, id=order_id)  

        if order.status == 'waiting':  
            order.status = 'completed'  
            order.save()

    return render(request, 'admin/order_history.html', {'orders': orders})

@login_required(login_url='/login/')
def create_order_from_store(request):
    if not request.user.is_staff:
        return redirect('menu')  

    if request.method == 'POST':
        menu_id = request.POST.get('menu_id')  
        quantity = request.POST.get('quantity')  

        menu = Menu.objects.get(id=menu_id)
        total_price = menu.price * int(quantity)  

        Order.objects.create(
            user=request.user,
            menu=menu,
            quantity=int(quantity),
            total_price=total_price,
            status='success',  
            image=menu.image  
        )

        return redirect('order_history') 

    menus = Menu.objects.all()  
    return render(request, 'admin/order_from_store.html', {'menus': menus})