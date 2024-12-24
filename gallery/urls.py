from django.urls import path
from .views import upload_image, gallery_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', upload_image, name='upload_image'),
    path('gallery/', gallery_view, name='gallery'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
