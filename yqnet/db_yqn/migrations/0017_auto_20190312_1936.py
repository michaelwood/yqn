# Generated by Django 2.1 on 2019-03-12 19:36

import db_yqn.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db_yqn', '0016_grouppage_last_updated_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppagemedia',
            name='file_upload',
            field=models.FileField(upload_to=db_yqn.models.group_dir),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='file_upload',
            field=models.FileField(upload_to=db_yqn.models.user_dir),
        ),
    ]
