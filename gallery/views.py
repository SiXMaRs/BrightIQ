from django.shortcuts import render, redirect
from .models import Image
from .forms import ImageForm
import gradio as gr
from django.conf import settings

def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery')
    else:
        form = ImageForm()
    return render(request, 'gallery/upload_image.html', {'form': form})

def gallery_view(request):
    images = Image.objects.all()

    def show_gallery():
        images = Image.objects.all()
        urls = [f"http://127.0.0.1:8000{settings.MEDIA_URL}{image.image.name}" for image in images]
        return [[url, images.title] for url in urls]

    interface = gr.Interface(
        fn=show_gallery,
        inputs=[],
        outputs=gr.Gallery(label="Image Gallery", elem_id="gallery", columns=4)
    )

    return render(request, 'gallery/gallery_view.html', {'gradio_interface': interface})
