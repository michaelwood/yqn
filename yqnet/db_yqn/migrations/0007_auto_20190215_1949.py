# Generated by Django 2.1 on 2019-02-15 19:49

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    atomic=False
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db_yqn', '0006_auto_20190214_1727'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserPage',
            new_name='GroupPage',
        ),
    ]