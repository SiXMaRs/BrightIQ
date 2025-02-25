from django.urls import path
from .views import *

urlpatterns = [
    path('', gradio_view, name='gradio_app'),
]