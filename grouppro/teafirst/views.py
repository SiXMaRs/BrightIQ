from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
import json
from django.core.paginator import Paginator
from .forms import *
from .models import *
import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.io as pio
from django.db.models import Sum,Count
from django.db.models.functions import TruncMonth, TruncDay
import threading

import calendar


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('menu')  
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

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

@login_required
def add_to_cart(request, menu_id):
    menu_item = get_object_or_404(Menu, id=menu_id)
    user = request.user

    if request.method == 'POST':
        topping_ids = request.POST.getlist('toppings')
        selected_toppings = Topping.objects.filter(id__in=topping_ids)

        cart_item = Cart(user=user, menu=menu_item, quantity=1)
        cart_item.save()

        cart_item.toppings.add(*selected_toppings)

        topping_price = sum(topping.price for topping in selected_toppings)
        cart_item.total_price = (menu_item.price + topping_price) * cart_item.quantity
        cart_item.save()

        return redirect('cart')

    return render(request, 'user/add_to_cart.html', {'menu_item': menu_item, 'toppings': Topping.objects.all()})

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_cost = 0 

    for item in cart_items:
        topping_price = sum(topping.price for topping in item.toppings.all())  
        item.total_price = item.quantity * (item.menu.price + topping_price)  
        item.save()
        
        total_cost += item.total_price  

    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total_cost': total_cost})


@login_required
def update_cart_quantity(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if action == "increase":
        cart_item.quantity += 1  
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1  

    topping_price = sum(topping.price for topping in cart_item.toppings.all())
    cart_item.total_price = cart_item.quantity * (cart_item.menu.price + topping_price)

    cart_item.save()  
    return redirect('cart')  

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def place_order(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items:
        return redirect('cart_view')

    for item in cart_items:
        total_price = item.total_price

        menu_image = item.menu.image if item.menu.image else None

        order = Order.objects.create(
            user=user,
            menu=item.menu,
            quantity=item.quantity,
            total_price=total_price,
            status='waiting'
        )

        if menu_image:
            order.image = menu_image
        
        order.toppings.set(item.toppings.all()) 
        order.save() 

    cart_items.delete()

    return redirect('menu')

@login_required(login_url='/login/')
def user_order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at') 
    return render(request, 'user/order_user.html', {'orders': orders})




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

    menus = Menu.objects.all().order_by('-id')  
    paginator = Paginator(menus, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/list_menu.html', {'form': form, 'page_obj': page_obj})

@login_required(login_url='/login/')
def edit_menu_view(request):
    if not request.user.is_staff:
        return redirect('menu')

    if request.method == 'POST':
        menu_id = request.POST.get('menu_id')
        menu = get_object_or_404(Menu, id=menu_id)
        form = MenuForm(request.POST, request.FILES, instance=menu) 
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

    orders = Order.objects.all().order_by('-ordered_at')  
    paginator = Paginator(orders, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        if order.status == 'waiting':
            order.status = 'completed'
            order.save()

    return render(request, 'admin/order_history.html', {'page_obj': page_obj})

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
            status='completed',
            image=menu.image  
        )

        return redirect('order_history') 

    menus = Menu.objects.all()  
    return render(request, 'admin/order_from_store.html', {'menus': menus})


def get_sales_data():
    print("🔄 กำลังดึงข้อมูลยอดขาย 7 วันล่าสุด...")

    # ✅ ดึงข้อมูลแบบ raw (values_list) แทน annotate
    raw_data = list(Order.objects.values_list("ordered_at", "total_price"))

    if not raw_data:
        print("⚠️ ไม่มีข้อมูลยอดขาย!")
        return pd.DataFrame({"Day": [], "Total Sales": [], "Text Display": []})

    # สร้าง DataFrame จาก raw_data
    df = pd.DataFrame(raw_data, columns=["ordered_at", "Total Sales"])

    # แปลง ordered_at เป็นวันที่เท่านั้น
    df["Day"] = pd.to_datetime(df["ordered_at"]).dt.strftime("%Y-%m-%d")

    # กรองข้อมูลให้เป็น 7 วันล่าสุด
    today = pd.to_datetime("today").normalize()
    last_7_days = pd.date_range(end=today, periods=7, freq="D").strftime("%Y-%m-%d")
    
    # รวมยอดขายต่อวัน (เฉพาะตัวเลข)
    df = df.groupby("Day", as_index=False)[["Total Sales"]].sum()

    # สร้าง DataFrame สำหรับวันที่ครบทุกวัน (ถ้ามีวันไหนไม่มีข้อมูล ให้เป็น 0)
    df_full = pd.DataFrame({"Day": last_7_days})
    df = df_full.merge(df, on="Day", how="left").fillna({"Total Sales": 0}) 

    # แปลง Total Sales เป็น float และกำหนดค่า text แสดงผล
    df["Total Sales"] = df["Total Sales"].astype(float)
    df["Text Display"] = df["Total Sales"].apply(lambda x: f"{x:.2f} ฿")

    print("📊 DataFrame หลังเติม 7 วันล่าสุด:\n", df)
    return df

# ฟังก์ชันสร้างกราฟที่ถูกต้อง
def generate_charts():
    df = get_sales_data()

    if df.empty:
        print("ไม่มีข้อมูลยอดขาย")
        return (
            px.bar(title="No Sales Data"), 
            "ยอดขาย: 0 ฿", 
            {}
        )

    df = df.reset_index(drop=True)

    total_sales_month = df["Total Sales"].sum()
    total_sales_per_day = dict(zip(df["Day"], df["Total Sales"]))

    df["Day"] = df["Day"].astype(str)

    print("📊 DataFrame ที่ถูกส่งเข้า Plotly:\n", df.to_dict())
    bar_chart = px.bar(
        df,
        x="Day",
        y="Total Sales",  
        title="Daily Sales (Last 7 Days)",
        text=df["Text Display"],  
        hover_data={"Text Display": True},
        category_orders={"Day": sorted(df["Day"].unique())}
    )

    bar_chart.update_xaxes(type="category", categoryorder="array", categoryarray=sorted(df["Day"].unique()))
    bar_chart.update_yaxes(type="linear", range=[0, max(df["Total Sales"].max(), 10)])  
    bar_chart.update_layout(
        yaxis=dict(type="linear", range=[0, df["Total Sales"].max() + 10])  
    )
    bar_chart.update_layout(
        title="ยอดขายรายวัน (7 วันล่าสุด)",  
        xaxis_title="วันที่", 
        yaxis_title="ยอดขาย (บาท)", 
    )
    bar_chart.update_traces(texttemplate='%{text}', textposition='outside')

    print("Charts Generated!")
    return (
        bar_chart,
        f"ยอดขายรวม 7 วัน: {total_sales_month:.2f} ฿",
        total_sales_per_day
    )

def gradio_dashboard():
    print("✅ กำลังรัน Gradio...")

    with gr.Blocks() as demo:
        gr.Markdown("ยอดขาย 7 วัน")

        bar_chart, total_sales_text, _ = generate_charts()

        bar_plot = gr.Plot(bar_chart)
        total_sales_display = gr.Textbox(value=total_sales_text, interactive=False, label="ยอดขายรวม 7 วัน")

    print(" Gradio Loaded!")
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, inline=False)

gradio_url = "http://127.0.0.1:7860/"
if not any(thread.name == "GradioThread" for thread in threading.enumerate()):
    print("เริ่มรัน Gradio บนพอร์ต 7860")
    thread = threading.Thread(target=gradio_dashboard, daemon=True, name="GradioThread")
    thread.start()

def get_today_stats():
    today = timezone.now().date()  
    orders_today = Order.objects.filter(ordered_at__date=today)
    total_sales_today = orders_today.aggregate(Sum('total_price'))['total_price__sum'] or 0
    count_orders_today = orders_today.count()

    return total_sales_today, count_orders_today

def dashboard(request):
    total_sales_today, count_orders_today = get_today_stats()
    
    context = {
        "gradio_url": gradio_url,
        "total_sales_today": total_sales_today,
        "count_orders_today": count_orders_today
    }
    return render(request, "dashboard/gradio_dashboard.html", context)