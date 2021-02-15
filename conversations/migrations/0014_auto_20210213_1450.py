# Generated by Django 3.1.6 on 2021-02-13 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0013_auto_20210213_1235'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='thread',
            options={'ordering': ['-last_updated']},
        ),
        migrations.AddField(
            model_name='thread',
            name='unread',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
