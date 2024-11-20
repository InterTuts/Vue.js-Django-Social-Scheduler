# System Utils
from django.db import models
from datetime import datetime

# App Utils
from authentication.models import CustomUser
from networks.models import NetworksModel

class PostsModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True)
    published = models.BooleanField(default=False)
    scheduled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now, blank=True, null=True)

    class Meta:
        db_table = 'posts'

    def __str__(self):
        return self.text[:50]
    
class PostsNetworksModel(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(PostsModel, on_delete=models.CASCADE, null=True)
    network = models.ForeignKey(NetworksModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'posts_networks'

    def __str__(self):
        return self.id