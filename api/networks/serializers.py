# Installed Utils
from rest_framework import serializers

# App Utils
from .models import NetworksModel

# Serializer for accounts list
class NetworksModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworksModel
        fields = '__all__'