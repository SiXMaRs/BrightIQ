import gradio as gr
import pandas as pd


# สร้างข้อมูลใหม่
sales_data = pd.DataFrame({
    "Product": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    "Sales": [150, 200, 300, 100, 250],
    "Region": ["North", "South", "East", "West", "North"]
})

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

        # อัปเดต Bar Chart
        def update_charts(sort_option):
            if sort_option == "Ascending":
                sorted_data = sales_data.sort_values(by="Sales")
            elif sort_option == "Descending":
                sorted_data = sales_data.sort_values(by="Sales", ascending=False)
            else:
                sorted_data = sales_data

            return (
                gr.BarPlot(value=sorted_data, x="Product", y="Sales", color="Region"),
                gr.LinePlot(value=sorted_data, x="Product", y="Sales", color="Region")
            )

    # รัน Gradio App
    _, local_url, _ = demo.launch(share=False, inline=False, prevent_thread_lock=True)
    return local_url

