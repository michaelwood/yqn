# Generated by Django 2.1 on 2019-02-18 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db_yqn', '0009_auto_20190218_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venue',
            name='lat_lng',
        ),
    ]