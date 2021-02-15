# Generated by Django 3.1.6 on 2021-02-12 18:58

from django.db import migrations, models
import conversations.models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0003_attachment_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='receivedmessage',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterField(
            model_name='attachment',
            name='content',
            field=models.FileField(upload_to=conversations.models.upload_to_location),
        ),
        migrations.AlterField(
            model_name='receivedmessage',
            name='cc',
            field=models.TextField(null=True),
        ),
    ]
