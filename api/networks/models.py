# System Utils
from django.db import models

# App Utils
from authentication.models import CustomUser

class NetworksModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='networks')
    network_name = models.CharField(max_length=50)
    net_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    token = models.TextField()
    secret = models.TextField(null=True)

    class Meta:
        db_table = 'networks'

    def __str__(self):
        return self.name