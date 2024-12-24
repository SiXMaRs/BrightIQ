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

# สร้าง Gradio Interface
def get_gradio_link():
    with gr.Blocks() as demo:
        gr.Markdown("### Interactive Bar Plot Example")
        
        sort_option = gr.Radio(
            choices=["None", "Ascending", "Descending"],
            value="None",
            label="Sort by Sales"
        )
        
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
        
        sort_option.change(
            bar_plot,
            inputs=[sort_option],
            outputs=bar_plot_output
        )

    # เปิด Gradio และรับลิงก์ iframe
    _, local_url, _ = demo.launch(share=False, prevent_thread_lock=True)
    return local_url

