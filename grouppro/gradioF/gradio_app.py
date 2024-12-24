import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.io as pio

# ตั้งค่าธีมเริ่มต้น
pio.templates.default = "plotly_dark"

# สร้างข้อมูลใหม่
sales_data = pd.DataFrame({
    "Product": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    "Sales": [15554000, 26580000, 39658000, 44504000, 50588000],
    "Region": ["North", "South", "East", "West", "North"]
})

# ฟังก์ชันสร้าง Pie Chart
def pie_chart():
    pie_data = sales_data.groupby("Region").sum().reset_index()
    fig = px.pie(
        pie_data,
        values="Sales",
        names="Region",
        title="Sales Distribution by Region",
        template="plotly_dark"  # ใช้ธีมสีเดียวกับ Bar Chart และ Line Chart
    )
    return fig

# ฟังก์ชันสร้าง Bar Plot
def bar_plot(sort_option):
    if sort_option == "Ascending":
        sorted_data = sales_data.sort_values(by="Sales")
    elif sort_option == "Descending":
        sorted_data = sales_data.sort_values(by="Sales", ascending=False)
    else:
        sorted_data = sales_data

    return gr.BarPlot(
        value=sorted_data,
        x="Product",
        y="Sales",
        color="Region",
        title="Sales by Product and Region",
        x_title="Products",
        y_title="Sales (Units)",
        color_legend_title="Region"
    )

# ฟังก์ชันสร้าง Line Plot
def line_plot(sort_option):
    if sort_option == "Ascending":
        sorted_data = sales_data.sort_values(by="Sales")
    elif sort_option == "Descending":
        sorted_data = sales_data.sort_values(by="Sales", ascending=False)
    else:
        sorted_data = sales_data

    return gr.LinePlot(
        value=sorted_data,
        x="Product",
        y="Sales",
        color="Region",
        title="Sales Trend by Product and Region",
        x_title="Products",
        y_title="Sales (Units)",
        color_legend_title="Region"
    )

# สร้าง Gradio Interface
def get_gradio_link():
    with gr.Blocks() as demo:
        gr.Markdown("### Interactive Chart Example")

        # Bar Chart
        bar_chart = gr.BarPlot(
            value=sales_data,
            x="Product",
            y="Sales",
            color="Region",
            title="Bar Chart: Sales by Product",
            x_title="Products",
            y_title="Sales (Units)",
            color_legend_title="Region"
        )

        # Line Chart
        line_chart = gr.LinePlot(
            value=sales_data,
            x="Product",
            y="Sales",
            color="Region",
            title="Line Chart: Sales Trend",
            x_title="Products",
            y_title="Sales (Units)",
            color_legend_title="Region"
        )

        # Pie Chart
        pie_chart_plot = gr.Plot(pie_chart())

        # จัดเรียงองค์ประกอบในหน้า Gradio
        with gr.Row():
            bar_chart
            line_chart
            pie_chart_plot

    # รัน Gradio App
    _, local_url, _ = demo.launch(share=False, inline=False, prevent_thread_lock=True)
    return local_url
