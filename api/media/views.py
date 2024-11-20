# System Utils
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _

# Installed Utils
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# App Utils
from .services import Imgur

def validate_image_format(image):
    allowed_extensions = ['jpg', 'jpeg', 'png']
    allowed_mime_types = ['image/jpeg', 'image/png']

    # Check file extension
    file_extension = image.name.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        return False

    # Check MIME type
    mime_type = image.content_type.lower()
    if mime_type not in allowed_mime_types:
        return False

    return True

class UploadImageView(CreateAPIView):

    # No serializer used
    serializer_class = None

    # Queryset is none
    queryset = None

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        try:

            # Get the image
            image = request.FILES.get('image')

            # Validate file type
            if not validate_image_format(image):
                return Response(
                    {
                        "success": False,
                        "message": "Invalid image format. Only JPG and PNG allowed."
                    },
                    status=status.HTTP_200_OK
                )
            
            # Save image on server
            image_path = default_storage.save(image.name, image)

            # Upload image to Imgur
            #Imgur().upload(image=image)

            return Response(
                {
                    "success": True,
                    "message": _('The image was saved successfully.'),
                    "content": {
                        "path": 'uploads/' + image_path
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e)
                },
                status=status.HTTP_200_OK
            )