# System Utils
from django.utils.translation import gettext_lazy as _

# Installed Utils
from rest_framework import serializers

# App Utils
from .models import PostsModel, PostsNetworksModel
from networks.models import NetworksModel

# Serializer for account
class NetworkSerializer(serializers.Serializer):

    # Fields for serialization
    id = serializers.IntegerField()
    network_name = serializers.CharField()

# Define a nested serializer for the scheduledTime
class ScheduledSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.CharField(max_length=2)
    date = serializers.CharField(max_length=2)
    hours = serializers.CharField(max_length=2)
    minutes = serializers.CharField(max_length=2)

# Serializer for registration
class PostSerializer(serializers.ModelSerializer):

    # Fields for serialization
    text: str = serializers.CharField(max_length=1200)
    image: str = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    networks = serializers.ListField(
        child=NetworkSerializer(),
        allow_empty=False
    )
    scheduled = ScheduledSerializer(required=False, allow_null=True)

    class Meta:
        model = PostsModel
        fields = ['text', 'image', 'networks', 'scheduled'] 

    def validate_networks(self, networks) -> str:
        """
        Validate the networks fields
        """
        
        # Verify if networks missing
        if len(networks) == 0:
            raise serializers.ValidationError(_('No networks were selected.'))
        
        return networks

class PostsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostsModel
        fields = ['id', 'user', 'text', 'image', 'published', 'scheduled', 'created_at']

class NetworksSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworksModel
        fields = ['id', 'network_name', 'net_id', 'name', 'token', 'secret']

class PostsNetworksSerializer(serializers.ModelSerializer):
    network = NetworksSerializer()
    class Meta:
        model = PostsNetworksModel
        fields = ['network']

class PostDetailsSerializer(serializers.ModelSerializer):
    networks = PostsNetworksSerializer(source='postsnetworksmodel_set', many=True)
    class Meta:
        model = PostsModel
        fields = ['id', 'user', 'text', 'image', 'published', 'scheduled', 'created_at', 'networks']