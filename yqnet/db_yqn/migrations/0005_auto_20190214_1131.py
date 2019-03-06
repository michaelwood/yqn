# Generated by Django 2.1 on 2019-02-14 11:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('db_yqn', '0004_auto_20190212_2323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='date_start',
        ),
        migrations.RemoveField(
            model_name='event',
            name='date_to',
        ),
        migrations.RemoveField(
            model_name='event',
            name='time_end',
        ),
        migrations.RemoveField(
            model_name='event',
            name='time_start',
        ),
        migrations.AddField(
            model_name='event',
            name='date_time_end',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='date_time_start',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]