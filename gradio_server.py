import os
import django

# กำหนด DJANGO_SETTINGS_MODULE ให้ชี้ไปที่ settings.py ของโปรเจกต์
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gradio_gallery.settings')

# เริ่มต้น Django
django.setup()

import gradio as gr
from gallery.models import Image

# ฟังก์ชันสำหรับดึงข้อมูลภาพ
def show_gallery():
    images = Image.objects.all()
    return [[image.image.url, image.title] for image in images]

# สร้าง Gradio Interface
interface = gr.Interface(
    fn=show_gallery,
    inputs=[],
    outputs=gr.Gallery(label="Image Gallery", columns=4),
)

# รันเซิร์ฟเวอร์ Gradio
if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860)
