from django.shortcuts import redirect,render
from .gradio_app import *

def gradio_view(request):
    gradio_url = get_gradio_link()
    return render(request, 'gradio_template.html', {'gradio_url': gradio_url})


