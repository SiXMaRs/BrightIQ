import gradio as gr

def greet(name):
    return f"สวัสดี, {name}!"

iface = gr.Interface(fn=greet, inputs="text", outputs="text")
iface.launch(server_name="127.0.0.1", server_port=7860)
