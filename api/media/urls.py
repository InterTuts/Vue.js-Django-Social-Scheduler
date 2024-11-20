# System Utils
from django.urls import path

# App Utils
from .views import UploadImageView

# Namespace for the media app
app_name='media'

urlpatterns = [
    path('upload-image', UploadImageView.as_view(), name='upload_image')
]