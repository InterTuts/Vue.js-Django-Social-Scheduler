# System Utils
from ast import Set
import time
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlencode

# Installed Utils
import requests
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# App Utils
from authentication.models import CustomUser
from .models import NetworksModel
from .serializers import NetworksModelSerializer

class ConnectView(APIView):

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        # Get the network's slug
        slug = kwargs.get('slug')
        
        # Verify if is facebook pages
        if slug == 'facebook_pages':
        
            # Permissions to request
            permissions = [
                'pages_show_list',
                'pages_manage_posts',
                'business_management'
            ]

            # Prepare parameters for URL
            params = {
                'client_id': settings.FACEBOOK_APP_ID,
                'state': str(int(time.time())),
                'response_type': 'code',
                'redirect_uri': request.build_absolute_uri('networks/callback/facebook'),
                'scope': ','.join(permissions),
            }

            # Set URL
            the_url = f"https://www.facebook.com/{settings.FACEBOOK_API_VERSION}/dialog/oauth" + "?" + urlencode(params)
        
            return Response(
                {
                    "success": True,
                    "content": the_url
                },
                status=status.HTTP_200_OK
            )
        
        else:

            # Permissions to request
            permissions = [
                'threads_basic',
                'threads_content_publish'
            ]
            
            # Prepare parameters for URL
            params = {
                'client_id': settings.THREADS_APP_ID,
                'state': str(int(time.time())),
                'response_type': 'code',
                'redirect_uri': request.build_absolute_uri('networks/callback/threads'),
                'scope': ','.join(permissions),
            }

            # Set URL
            the_url = f"https://threads.net/oauth/authorize" + "?" + urlencode(params)
        
            return Response(
                {
                    "success": True,
                    "url": the_url
                },
                status=status.HTTP_200_OK
            )            
    
class CallbackView(APIView):

    # Authentication class to authenticate the user by token
    authentication_classes = [TokenAuthentication]

    # Class to verify if the user is authenticated
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        # Get the network's slug
        slug = kwargs.get('slug')

        try:

            if slug == 'facebook_pages':
                
                # Prepare the fields
                fields = {
                    'client_id': settings.FACEBOOK_APP_ID,
                    'client_secret': settings.FACEBOOK_APP_SECRET,
                    'grant_type': 'authorization_code',
                    'redirect_uri': request.build_absolute_uri('networks/callback/facebook'),
                    'code': request.GET.get('code')
                }

                # Send the POST request to Facebook's OAuth endpoint
                url = f'https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/oauth/access_token'
                response = requests.post(url, data=fields, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})

                # Check if the access token exists
                if response.status_code == 200:

                    # Convert json into a list
                    access_token_data = response.json()

                    # Fetch Facebook Pages
                    request_url = f'https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/accounts'
                    request_params = {
                        'limit': 500,
                        'access_token': access_token_data['access_token']
                    }
                    accounts = requests.get(request_url, params=request_params).json().get('data', [])

                    # Verify if accounts exists
                    if ( len(accounts) != 0 ):

                        # Get the user instance
                        user_instance = CustomUser.objects.get(id=request.user.id)

                        # Get all saved Facebook Pages
                        networks = user_instance.networks.filter(network_name='facebook_pages')

                        # Convert the networks queryset to a list
                        networks_list = list(networks)

                        # Get only the accounts values
                        net_ids_list = list(networks.values_list('net_id', flat=True))

                        # Networks Container for Saving
                        networks_save = []
                        
                        # List the pages
                        for account in accounts:

                            # Check if the page is saved
                            if account.get('id') in net_ids_list:

                                # Get the net id index
                                net_id_index = net_ids_list.index(account.get('id'))
                                
                                # Update the page's name
                                networks_list[net_id_index].name = account.get('name')

                                # Update the page's token
                                networks_list[net_id_index].token = account.get('access_token')
                                
                            else:
                                networks_save.append(NetworksModel(
                                    user=user_instance,
                                    network_name='facebook_pages',
                                    net_id=account.get('id'),
                                    name=account.get('name'),
                                    token=account.get('access_token')
                                ))

                        # Delete cache
                        cache.delete(f"user_last_networks_{self.request.user.id}")
                    
                        # Verify if saved pages exists
                        if len(networks) > 0:

                            # Update Facebook Pages
                            NetworksModel.objects.bulk_update(networks_list, ['name', 'token']) 

                        if len(networks_save) > 0:

                            # Save Facebook Pages
                            NetworksModel.objects.bulk_create(networks_save)

                        return Response(
                            {
                            "success": True,
                            "message": _('All selected pages were connected successfully.')
                            },
                            status=status.HTTP_200_OK
                        )    
                            
                    return Response(
                        {
                            "success": False,
                            "message": _('No pages were found.')
                        },
                        status=status.HTTP_200_OK
                    )
                
                # Convert json into a list
                response_data = response.json().get('error', {})

                return Response(
                    {
                        "success": False,
                        "message": response_data['message']
                    },
                    status=status.HTTP_200_OK
                )
            
            elif slug == 'threads':

                # Prepare the fields
                fields = {
                    'client_id': settings.THREADS_APP_ID,
                    'client_secret': settings.THREADS_APP_SECRET,
                    'grant_type': 'authorization_code',
                    'redirect_uri': request.build_absolute_uri('networks/callback/threads'),
                    'code': request.GET.get('code')
                }

                # Send the POST request to Threads's OAuth endpoint
                url = f'https://graph.threads.net/oauth/access_token'
                response = requests.post(url, data=fields, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})

                # Check if the access token exists
                if response.status_code == 200:

                    # Convert json into a list
                    access_token_data = response.json()

                    # Fetch Threads account
                    request_url = f"https://graph.threads.net/{settings.THREADS_API_VERSION}/me?fields=id,username,name"
                    request_params = {
                        'access_token': access_token_data['access_token']
                    }
                    
                    # Get account's data
                    account = requests.get(request_url, params=request_params).json()

                    # Get the user instance
                    user_instance = CustomUser.objects.get(id=request.user.id)

                    # Get all saved accounts
                    networks = user_instance.networks.filter(network_name='threads')

                    # Convert the networks queryset to a list
                    networks_list = list(networks)

                    # Get only the accounts values
                    net_ids_list = list(networks.values_list('net_id', flat=True))

                    # Networks Container for Saving
                    networks_save = []

                    # Check if the page is saved
                    if account.get('id') in net_ids_list:

                        # Get the net id index
                        net_id_index = net_ids_list.index(account.get('id'))
                        
                        # Update the page's name
                        networks_list[net_id_index].name = account.get('name')

                        # Update the page's token
                        networks_list[net_id_index].token = access_token_data['access_token']
                        
                    else:
                        networks_save.append(NetworksModel(
                            user=user_instance,
                            network_name='threads',
                            net_id=account.get('id'),
                            name=account.get('name'),
                            token=access_token_data['access_token']
                        ))

                    # Delete cache
                    cache.delete(f"user_last_networks_{self.request.user.id}")
                
                    # Verify if saved pages exists
                    if len(networks) > 0:

                        # Update Facebook Pages
                        NetworksModel.objects.bulk_update(networks_list, ['name', 'token']) 

                    if len(networks_save) > 0:

                        # Save Facebook Pages
                        NetworksModel.objects.bulk_create(networks_save)

                    return Response(
                        {
                        "success": True,
                        "message": _('The threads account was connected successfully.')
                        },
                        status=status.HTTP_200_OK
                    )                     

                # Convert json into a list
                response_data = response.json().get('error', {})

                return Response(
                    {
                        "success": False,
                        "message": response_data['message']
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
        
class NetworksLastView(ListAPIView):

    # No serializer used
    serializer_class = NetworksModelSerializer

    # Queryset is none
    queryset = NetworksModel.objects.all()

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

        try:

            # Retrieve the last networks
            user_networks: Set[str] = cache.get(f"user_last_networks_{self.request.user.id}", set())

            # Check if cache exists
            if len(user_networks) != 0:
                # Return success message
                return Response(
                    {
                        "success": True,
                        "content": user_networks
                    },
                    status=status.HTTP_200_OK
                )

            # Retrieve the filtered queryset
            queryset = self.get_queryset()

            # Order queryset
            queryset = queryset.order_by('-id')[:5]

            # Get serialized data
            serializer = self.get_serializer(queryset, many=True)

            # Verify if accounts exists
            if queryset.count():

                # Save cache
                cache.set(f"user_last_networks_{self.request.user.id}", serializer.data, timeout=86400)

                return Response(
                    {
                        "success": True,
                        "content": serializer.data
                    },
                    status=status.HTTP_200_OK
                )

            else:

                return Response(
                    {
                        "success": False,
                        "message": _('No accounts were found.')
                    },
                    status=status.HTTP_200_OK
                )
            
        except Exception as e:

            return Response(
                {
                    "success": False,
                    "message": _(f"An error occurred: {e}")
                },
                status=status.HTTP_200_OK
            )

class NetworksListView(ListAPIView):

    # No serializer used
    serializer_class = NetworksModelSerializer

    # Queryset is none
    queryset = NetworksModel.objects.all()

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

        try:

            # Retrieve the filtered queryset
            queryset = self.get_queryset()

            # Order queryset
            queryset = queryset.order_by('-id')

            # Get serialized data
            serializer = self.get_serializer(queryset, many=True)

            # Verify if accounts exists
            if queryset.count():

                return Response(
                    {
                        "success": True,
                        "content": serializer.data
                    },
                    status=status.HTTP_200_OK
                )

            else:

                return Response(
                    {
                        "success": False,
                        "message": _('No accounts were found.')
                    },
                    status=status.HTTP_200_OK
                )
            
        except Exception as e:

            return Response(
                {
                    "success": False,
                    "message": _(f"An error occurred: {e}")
                },
                status=status.HTTP_200_OK
            )
        
class NetworksDeleteView(DestroyAPIView):
    # No serializer used
    serializer_class = None

    # Queryset is none
    queryset = NetworksModel.objects.all()

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

    def delete(self, request, *args, **kwargs):

        try:

            # Get the account's id
            id = kwargs.get('id')

            # Retrieve the filtered queryset
            queryset = self.get_queryset().filter(id=id)

            # Check if the object exists and delete it
            if queryset.exists():

                # Delete account
                queryset.delete()

                # Delete cache
                cache.delete(f"user_last_networks_{self.request.user.id}")

                return Response(
                    {
                        "success": True,
                        "message": _('The account was deleted successfully.')
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": _('The account was not deleted successfully.')
                    },
                    status=status.HTTP_200_OK
                )
            
        except Exception as e:

            return Response(
                {
                    "success": False,
                    "message": _(f"An error occurred: {e}")
                },
                status=status.HTTP_200_OK
            )