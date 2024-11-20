# System Utils
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import urllib.parse

# Installed Utils
import requests
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# App Utils
from .serializers import PostSerializer, PostsListSerializer, PostDetailsSerializer
from .models import PostsModel, PostsNetworksModel
from .pagination import DefaultPagination
from .cache import CacheManager
from .utils import NetworkObj, PostObj
from authentication.models import CustomUser
from networks.models import NetworksModel

class CreatePostView(CreateAPIView):

    # No serializer used
    serializer_class = PostSerializer

    # Queryset is none
    queryset = None

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs): 

        # Get information about serialization
        serializer = self.get_serializer(data=request.data)
        
        # Check if the received data is correct
        if not serializer.is_valid():

            # Default error message
            errorMsg: str = _('An error has occurred.')

            # Check if the error is for text
            if ( serializer.errors.get('text') != None ):
                errorMsg = serializer.errors['text'][0].capitalize()
            elif ( serializer.errors.get('image') != None ):
                errorMsg = serializer.errors['image'][0].capitalize()
            elif ( serializer.errors.get('networks') != None ):
                errorMsg = serializer.errors['networks'][0].capitalize()

            return Response(
                {
                    "success": False,
                    "message": errorMsg
                },
                status=status.HTTP_200_OK
            )
    
        try:

            # Get text
            text = serializer.validated_data.get('text')

            # Get the image
            image = serializer.validated_data.get('image')    

            # Get all networks accounts
            accounts = serializer.validated_data.get('networks')

            # Get the user instance
            user_instance = CustomUser.objects.get(id=request.user.id)

            # Convert it to a datetime object
            dt_obj = datetime.now()

            # Add timezone
            dt_with_timezone = timezone.make_aware(dt_obj)

            # New post's data
            new_post = PostsModel(
                user=user_instance,
                text=text,
                image=image,
                created_at=dt_with_timezone
            )

            # Save the post to the database
            new_post.save()

            # Create a cache manager instance
            cache_manager = CacheManager(user_id=self.request.user.id)

            # Clear all user's cached pages
            cache_manager.clear_cache()

            # Get post
            post = PostsModel.objects.get(id=new_post.id)

            # Publish count
            publish_count = 0

            # List the accounts
            for account in accounts:
                # Get network
                network = NetworksModel.objects.get(id=account['id'])

                # Prepare the posts network
                post_net = PostsNetworksModel(
                    post=post,
                    network=network
                )

                # Save posts network
                post_net.save()

                # Network data
                network_obj = NetworkObj(network.network_name, network.net_id, network.name, network.token, network.secret)

                # Posts data
                post_obj = PostObj(text, image)

                # Set post and account's data
                post_create = CreatePost(post_obj, network_obj)

                # Publish post
                publish = post_create.create_post()

                # Check if the post was published
                if publish['success']:
                    publish_count+=1

            if publish_count:
                return Response(
                    {
                        "success": True,
                        "message": _('The post was created successfully.')
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": _('The post was not created successfully.')
                    },
                    status=status.HTTP_200_OK
                )                 

        except CustomUser.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": _('User with the given ID does not exist.')
                },
                status=status.HTTP_200_OK
            )  
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"An error occurred: {e}"
                },
                status=status.HTTP_200_OK
            )
        
class SchedulePostView(CreateAPIView):

    # No serializer used
    serializer_class = PostSerializer

    # Queryset is none
    queryset = None

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs): 

        # Get information about serialization
        serializer = self.get_serializer(data=request.data)

        # Check if the received data is correct
        if not serializer.is_valid():

            # Default error message
            errorMsg: str = _('An error has occurred.')

            # Check if the error is for text
            if ( serializer.errors.get('text') != None ):
                errorMsg = serializer.errors['text'][0].capitalize()
            elif ( serializer.errors.get('image') != None ):
                errorMsg = serializer.errors['image'][0].capitalize()
            elif ( serializer.errors.get('networks') != None ):
                errorMsg = serializer.errors['networks'][0].capitalize()

            return Response(
                {
                    "success": False,
                    "message": errorMsg
                },
                status=status.HTTP_200_OK
            )
    
        try:

            # Get text
            text = serializer.validated_data.get('text')

            # Get the image
            image = serializer.validated_data.get('image')    

            # Get all networks accounts
            accounts = serializer.validated_data.get('networks')

            # Get scheduled time
            scheduled = serializer.validated_data.get('scheduled')           

            # Get the user instance
            user_instance = CustomUser.objects.get(id=request.user.id)

            # Your original datetime string
            dt_str = f"{scheduled['year']}-{scheduled['month']}-{scheduled['date']} {scheduled['hours']}:{scheduled['minutes']}:00.{datetime.now().microsecond:06d}"

            # Convert it to a datetime object
            dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")

            # Add timezone
            dt_with_timezone = timezone.make_aware(dt_obj)

            # Get the user instance
            user_instance = CustomUser.objects.get(id=request.user.id)

            # New post's data
            new_post = PostsModel(
                user=user_instance,
                text=text,
                image=image,
                scheduled=True,
                created_at=dt_with_timezone
            )

            # Save the post to the database
            new_post.save()

            # Create a cache manager instance
            cache_manager = CacheManager(user_id=self.request.user.id)

            # Clear all user's cached pages
            cache_manager.clear_cache()

            # Get post
            post = PostsModel.objects.get(id=new_post.id)

            # Publish count
            publish_count = 0

            # List the accounts
            for account in accounts:
                # Get network
                network = NetworksModel.objects.get(id=account['id'])

                # Prepare the posts network
                post_net = PostsNetworksModel(
                    post=post,
                    network=network
                )

                # Save posts network
                post_net.save()

                # Check if the post was saved
                if post_net.id is not None:
                    publish_count+=1

            if publish_count:
                return Response(
                    {
                        "success": True,
                        "message": _('The post was scheduled successfully.')
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": _('The post was not scheduled successfully.')
                    },
                    status=status.HTTP_200_OK
                )                 

        except CustomUser.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": _('User with the given ID does not exist.')
                },
                status=status.HTTP_200_OK
            )  
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"An error occurred: {e}"
                },
                status=status.HTTP_200_OK
            )
        
class PostsListView(ListAPIView):

    # Posts List Serializer
    serializer_class = PostsListSerializer

    # Queryset is none
    queryset = PostsModel.objects.all()

    # Pagination class with parameters
    pagination_class = DefaultPagination

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        return queryset

    def list(self, request, *args, **kwargs):

        # Create a cache manager instance
        cache_manager2 = CacheManager(user_id=self.request.user.id)

        # Clear all user's cached pages
        cache_manager2.clear_cache()

        # Create a cache manager instance
        cache_manager = CacheManager(user_id=self.request.user.id, page_number=request.GET.get('page', None))

        # Get the cache data
        cache = cache_manager.get_cache()

        # Check if cache exists
        if cache is not None: 
            # Set current time
            cache['content']['current_time'] = int(datetime.now().timestamp())
            # Return success message
            return Response(
                cache,
                status=status.HTTP_200_OK
            )

        # Apply queryset filtering
        queryset = self.filter_queryset(self.get_queryset())

        # Order queryset
        queryset = queryset.order_by('-id')

        # Get results
        results = self.paginate_queryset(queryset)
        
        # Check if results exists
        if results is not None:
        
            # Access the page query parameter
            page = request.GET.get('page', None)
            
            # Get serialized data
            serializer = self.get_serializer(results, many=True)

            # Set the data in cache
            cache_manager.set_cache({
                "content": {
                    "items": serializer.data,
                    "total": queryset.count(),
                    "page": int(page),
                }
            })

            # Return success message
            return Response(
                {
                    "content": {
                        "items": serializer.data,
                        "total": queryset.count(),
                        "page": int(page),
                        "current_time": int(datetime.now().timestamp())
                    }
                },
                status=status.HTTP_200_OK
            ) 

        # Return error message
        return Response(
            {
                "success": False,
                "message": _('No posts were found.')
            },
            status=status.HTTP_200_OK
        ) 
    
class PostDetailsView(RetrieveAPIView):

    # Posts Details Serializer
    serializer_class = PostDetailsSerializer

    # Queryset is none
    queryset = PostsModel.objects.all()

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        else:
            queryset = queryset.none()
        return queryset.prefetch_related(
            'postsnetworksmodel_set__network'
        )

    def get(self, request, *args, **kwargs):

        # Get the post's ID
        id = kwargs.get('id')

        # Retrieve the post
        queryset = self.get_queryset().filter(id=id)

        try:

            # Serialize the data
            serializer = self.get_serializer(queryset, many=True)

            # Check if the post exists
            if len(serializer.data) == 0:
                # Return error message
                return Response(
                    {
                        "success": False,
                        "message": _('The post was not found.')
                    },
                    status=status.HTTP_200_OK
                )             

            # Return requested post
            return Response(
                {
                    "success": True,
                    "content": {
                        "id": serializer.data[0].get('id'),
                        "text": serializer.data[0].get('text'),
                        "image": serializer.data[0].get('image'),
                        "published": serializer.data[0].get('published'),
                        "scheduled": serializer.data[0].get('scheduled'),
                        "created_at": int(datetime.fromisoformat(serializer.data[0].get('created_at').replace('Z', '+00:00')).timestamp()),
                        "networks": serializer.data[0].get('networks')
                    }
                },
                status=status.HTTP_200_OK
            ) 

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": _('The post was not found.')
                },
                status=status.HTTP_200_OK
            ) 

class PostCancelView(RetrieveAPIView):
    # No serializer used
    serializer_class = None

    # Queryset is none
    queryset = PostsModel.objects.all()

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        else:
            queryset = queryset.none()

        return queryset

    def post(self, request, *args, **kwargs):

        # Get the post id
        id = kwargs.get('id')

        try:

            # Retrieve the post
            post = self.get_queryset().filter(id=id).first()

            # Verify if a post was found
            if not post:

                # Return error message
                return Response(
                    {
                        "success": False,
                        "message": _('The post was not found.')
                    },
                    status=status.HTTP_200_OK
                ) 

            # Update the scheduled status
            post.scheduled = False 

            # Save changes
            post.save()

            # Create a cache manager instance
            cache_manager = CacheManager(user_id=self.request.user.id)

            # Clear all user's cached pages
            cache_manager.clear_cache()

            return Response(
                {
                    "success": True,
                    "message": _('The scheduled post was cancelled successfully.')
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"An error occurred: {e}"
                },
                status=status.HTTP_200_OK
            )
    
class UploadFbImage:
    """
    Upload images on Facebook
    """
    def __init__(self, post_obj, network_obj):

        # Assign objects value to the instance attribute
        self.post_obj=post_obj
        self.network_obj=network_obj      

    def send_request(self):

        try:

            # Url for images upload
            url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{self.network_obj.net_id}/photos?access_token={self.network_obj.token}"

            # Header for requests
            headers = {
                "Content-Type": "application/json",
            }

            # Image data
            data = {
                "url": self.post_obj.image,
                "published": False
            }

            # Send request
            response = requests.post(url, headers=headers, json=data)

            # Check if the request was successful
            if response.status_code == 200:

                # Parse the response JSON
                response_data = response.json()

                # Extract the id and return success response
                return {
                    "success": True,
                    "id": response_data.get('id')
                }
            else:

                # Return error
                return {
                    "success": False,
                    "message": f"Error: {response.status_code}, {response.text}"
                }
            
        except requests.exceptions.RequestException as e:

            # Return error
            return {
                "success": False,
                "message": f"An error occurred: {e}"
            }

class CreatePost:
    """
    Create a post
    """
    def __init__(self, post_obj, network_obj):

        # Assign objects value to the instance attribute
        self.post_obj=post_obj
        self.network_obj=network_obj

    def prepare_data(self):

        # Post's data
        return {
            "message": self.post_obj.text,
            "published": True
        }
    
    def send_request(self, data):
        
        if self.network_obj.network_name == "facebook_pages": 

            # Url parameters
            url_params = {
                "access_token": self.network_obj.token
            }

            # Verify if the post contains an image
            if ( self.post_obj.image ):

                # Init upload
                image_upload = UploadFbImage(self.post_obj, self.network_obj)

                # Try to upload
                image_response = image_upload.send_request()

                # Check if image's id exists
                if image_response['success']:
                    image_id=image_response["id"]
                    url_params[f"attached_media[{image_id}]"] = f'{{"media_fbid":"{image_id}"}}'
        
            try:
                
                # Url for post creation
                url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{self.network_obj.net_id}/feed" + "?" + urllib.parse.urlencode(url_params)

                # Headers
                headers = {
                    "Content-Type": "application/json",
                }

                # Publish post
                response = requests.post(url, headers=headers, json=data)

                # Check if the request was successful
                if response.status_code == 200:

                    # Parse the response JSON
                    response_data = response.json()

                    # Extract the id and return response
                    return {
                        "success": True,
                        "id": response_data.get('id')
                    }
                
                else:

                    # Return error
                    return {
                        "success": False,
                        "message": f"Error: {response.status_code}, {response.text}"
                    }

            except requests.exceptions.RequestException as e:

                # Return error
                return {
                    "success": False,
                    "message": f"An error occurred: {e}"
                }
            
        elif self.network_obj.network_name == "threads":

            try:

                # Url parameters
                thread_url_params = {
                    "access_token": self.network_obj.token
                }

                # Verify if the post contains an image
                if ( self.post_obj.image ):
                    thread_url_params["media_type"] = "IMAGE"
                    thread_url_params["image_url"] = self.post_obj.image
                else:
                    thread_url_params["media_type"] = "TEXT"
                
                # Url for post creation
                url = f"https://graph.threads.net/{settings.THREADS_API_VERSION}/{self.network_obj.net_id}/threads" + "?" + urllib.parse.urlencode(thread_url_params)

                # Headers
                headers = {
                    "Content-Type": "application/json",
                }

                # Publish post
                thread_response = requests.post(url, headers=headers, json={
                    "text": self.post_obj.text
                })

                # Check if the request was successful
                if thread_response.status_code == 200:

                    # Parse the response JSON
                    thread_response_data = thread_response.json()

                    # Url parameters
                    publish_url_params = {
                        "creation_id": thread_response_data.get('id'),
                        "access_token": self.network_obj.token
                    }
                    
                    # Url for post creation
                    url = f"https://graph.threads.net/{settings.THREADS_API_VERSION}/{self.network_obj.net_id}/threads_publish" + "?" + urllib.parse.urlencode(publish_url_params)

                    # Headers
                    headers = {
                        "Content-Type": "application/json",
                    }

                    # Publish post
                    publish_response = requests.post(url, headers=headers)

                    # Check if the thread was published
                    if publish_response.status_code == 200:

                        # Extract the id and return response
                        return {
                            "success": True,
                            "id": thread_response_data.get('id')
                        }
                    
                    else:

                        # Return error
                        return {
                            "success": False,
                            "message": f"Error: {publish_response.status_code}, {publish_response.text}"
                        }
                
                else:

                    # Return error
                    return {
                        "success": False,
                        "message": f"Error: {thread_response.status_code}, {thread_response.text}"
                    }

            except requests.exceptions.RequestException as e:

                # Return error
                return {
                    "success": False,
                    "message": f"An error occurred: {e}"
                }             

    def create_post(self):

        # Get post's data
        data=self.prepare_data()

        # Send post's data
        response=self.send_request(data)

        # Return response
        return response
