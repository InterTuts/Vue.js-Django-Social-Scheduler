# Generated by Django 5.0.6 on 2024-10-26 18:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_postsnetworksmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='postsnetworksmodel',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.postsmodel'),
        ),
    ]
