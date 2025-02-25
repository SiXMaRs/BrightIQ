import gradio as gr
import pandas as pd


# สร้างข้อมูลใหม่
sales_data = pd.DataFrame({
    "Product": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    "Sales": [900, 1200, 3000, 1000, 2050],
    "Region": ["North", "South", "East", "West", "North"]
})

# สร้าง Gradio Interface
def get_gradio_link():
    with gr.Blocks() as demo:
        gr.Markdown("### Interactive Bar Plot Example")
        
        # แสดง Bar Plot โดยตรง
        bar_plot_output = gr.BarPlot(
            value=sales_data,
            x="Product",
            y="Sales",
            color="Region",
            title="Sales by Product and Region",
            x_title="Products",
            y_title="Sales (Units)",
            color_legend_title="Region"
        )

    # เปิด Gradio และรับลิงก์ iframe
    _, local_url, _ = demo.launch(share=False, prevent_thread_lock=True)
    return local_url



