# System Utils
from django.urls import path

# App Utils
from .views import ConnectView, CallbackView, NetworksLastView, NetworksListView, NetworksDeleteView

# Namespace for the networks app
app_name='networks'

urlpatterns = [
    path('connect/<slug:slug>/', ConnectView.as_view(), name='connect_accounts'),
    path('callback/<slug:slug>/', CallbackView.as_view(), name='get_token'),
    path('last', NetworksLastView.as_view(), name='last_networks'),
    path('list', NetworksListView.as_view(), name='list_networks'),
    path('<int:id>', NetworksDeleteView.as_view(), name='delete_account')
]