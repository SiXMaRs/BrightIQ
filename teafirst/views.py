from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import *
import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.io as pio
from django.db.models import Sum,Count
from django.db.models.functions import TruncMonth, TruncDay
from django.shortcuts import render
import threading
import calendar


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


# Gradio
# ตั้งค่าธีมของ Plotly
pio.templates.default = "plotly_dark"

# ✅ ฟังก์ชันดึงข้อมูลยอดขายตามเดือนและวัน
def get_sales_data(selected_month=None):
    print(f"🔄 กำลังดึงข้อมูลสำหรับเดือน: {selected_month}")

    data = (
        Order.objects.annotate(
            month=TruncMonth("ordered_at"),
            day=TruncDay("ordered_at")
        )
        .values("month", "day")
        .annotate(
            total_sales=Sum("total_price"),
            order_count=Count("id")
        )
        .order_by("day")
    )

    df = pd.DataFrame(list(data))

    if df.empty:
        print("⚠️ ไม่มีข้อมูลยอดขายในช่วงเวลานี้!")
        return pd.DataFrame({"Day": [], "Total Sales": [], "Order Count": []})

    df["Day"] = pd.to_datetime(df["day"]).dt.strftime("%Y-%m-%d")
    df.rename(columns={"total_sales": "Total Sales", "order_count": "Order Count"}, inplace=True)

    # ✅ กรองเฉพาะเดือนที่เลือก
    if selected_month and selected_month != "All":
        df = df[df["Day"].str.startswith(selected_month)]

        # ✅ สร้างช่วงวันที่ให้ครบทุกวันของเดือน
        year, month = map(int, selected_month.split("-"))
        num_days = calendar.monthrange(year, month)[1]  # ดึงจำนวนวันในเดือนนั้น
        all_days = pd.date_range(start=f"{selected_month}-01", periods=num_days, freq="D").strftime("%Y-%m-%d")
        df_full = pd.DataFrame({"Day": all_days})

        # ✅ รวมข้อมูลเข้ากับ `df` (ถ้าไม่มีค่า ให้ใส่ 0)
        df = df_full.merge(df, on="Day", how="left").fillna({"Total Sales": 0, "Order Count": 0})

    print("📊 DataFrame ที่ใช้สร้างกราฟ (หลังเติมข้อมูลครบเดือน):\n", df.head(10))  # ✅ แสดง 10 แถวแรก
    print(df.info())  # ✅ ตรวจสอบโครงสร้าง
    return df

# ✅ ฟังก์ชันสร้างกราฟ
def generate_charts(selected_month="All"):
    df = get_sales_data(selected_month)

    if df.empty:
        print("❌ ไม่มีข้อมูลสำหรับเดือนที่เลือก")
        return (
            px.bar(title="No Sales Data"), 
            px.line(title="No Sales Data"), 
            px.pie(title="No Sales Data"), 
            px.bar(title="No Orders Data"),
            "💰 Total Sales: 0 ฿ | 📦 Total Orders: 0", 
            {}, {}
        )

    df["Total Sales"] = df["Total Sales"].astype(float)  # ✅ บังคับเป็น float
    df["Order Count"] = df["Order Count"].astype(int)  # ✅ บังคับเป็น int

    total_sales_month = df["Total Sales"].sum()
    total_orders_month = df["Order Count"].sum()

    total_sales_per_day = dict(zip(df["Day"], df["Total Sales"]))
    total_orders_per_day = dict(zip(df["Day"], df["Order Count"]))

    df["Day"] = df["Day"].astype(str)  # ✅ บังคับให้เป็น string แก้ปัญหาแสดงเวลา 12:00

    # ✅ บังคับให้ Plotly เรียงลำดับวันถูกต้อง
    category_orders = {"Day": sorted(df["Day"].unique())}

    # ✅ Bar Chart (ยอดขายรายวัน)
    bar_chart = px.bar(
        df, x="Day", y="Total Sales", title=f"Daily Sales in {selected_month}",
        text=df["Total Sales"].astype(str), category_orders=category_orders
    )
    bar_chart.update_xaxes(type="category", categoryorder="array", categoryarray=sorted(df["Day"].unique()))
    bar_chart.update_traces(texttemplate='%{text} ฿', textposition='outside')

    # ✅ Line Chart (แนวโน้มยอดขาย)
    line_chart = px.line(
        df, x="Day", y="Total Sales", title=f"Sales Trend in {selected_month}",
        text=df["Total Sales"].astype(str), category_orders=category_orders
    )
    line_chart.update_xaxes(type="category", categoryorder="array", categoryarray=sorted(df["Day"].unique()))
    line_chart.update_traces(mode="lines+markers+text", textposition="top center", texttemplate='%{text} ฿')


    # ✅ Bar Chart (จำนวนคำสั่งซื้อรายวัน)
    order_chart = px.bar(
        df, x="Day", y="Order Count", title=f"Daily Order Count in {selected_month}",
        text=df["Order Count"].astype(str), category_orders={"Day": sorted(df["Day"].unique())}
    )
    order_chart.update_traces(texttemplate='%{text} Orders', textposition='outside')

    print("✅ Charts Generated!")

    return (
        bar_chart, line_chart, order_chart,
        f"💰 Total Sales: {total_sales_month:.2f} ฿ | 📦 Total Orders: {total_orders_month}",
        total_sales_per_day, total_orders_per_day
    )

# ✅ ฟังก์ชันสร้าง Gradio Dashboard
def gradio_dashboard():
    print("✅ กำลังรัน Gradio...")

    df = get_sales_data()
    available_months = ["All"] + sorted(df["Day"].str[:7].unique().tolist()) if not df.empty else ["All"]

    with gr.Blocks() as demo:
        gr.Markdown("### 📊 Sales & Orders Dashboard - Data from Database")

        selected_month = gr.Dropdown(choices=available_months, value="All", label="🔍 Select Month")

        bar_chart, line_chart, order_chart, total_sales, total_sales_per_day, total_orders_per_day = generate_charts("All")

        bar_plot = gr.Plot(bar_chart)
        line_plot = gr.Plot(line_chart)
        order_plot = gr.Plot(order_chart)
        total_sales_text = gr.Textbox(value=total_sales, interactive=False, label="💰 Total Sales & Orders")

        # ✅ อัปเดตเมื่อเลือกเดือน
        selected_month.change(
            generate_charts,
            inputs=[selected_month],
            outputs=[bar_plot, line_plot, order_plot, total_sales_text]
        )

    print("✅ Gradio Loaded!")
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, inline=False)


# ✅ รัน Gradio
gradio_url = "http://127.0.0.1:7860/"
if not any(thread.name == "GradioThread" for thread in threading.enumerate()):
    print("🚀 เริ่มรัน Gradio บนพอร์ต 7860")
    thread = threading.Thread(target=gradio_dashboard, daemon=True, name="GradioThread")
    thread.start()

def dashboard(request):
    return render(request, "dashboard/gradio_dashboard.html", {"gradio_url": gradio_url})