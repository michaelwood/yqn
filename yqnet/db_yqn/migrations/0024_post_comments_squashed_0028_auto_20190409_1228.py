# Generated by Django 2.1 on 2019-04-09 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('db_yqn', '0024_post_comments'), ('db_yqn', '0025_auto_20190408_1424'), ('db_yqn', '0026_auto_20190408_1427'), ('db_yqn', '0027_auto_20190408_2248'), ('db_yqn', '0028_auto_20190409_1228')]

    dependencies = [
        ('db_yqn', '0023_auto_20190402_1414_squashed_0025_auto_20190404_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comments',
            field=models.ManyToManyField(blank=True, to='db_yqn.Post'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(blank=True, default='', help_text='Title or Subject of Post', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='source',
            field=models.IntegerField(choices=[(0, 'Local Post'), (1, 'Blog'), (2, 'Podcast'), (3, 'News'), (4, 'Comment')], default=0),
        ),
        migrations.AlterField(
            model_name='xmlfeed',
            name='source',
            field=models.IntegerField(choices=[(1, 'Blog'), (2, 'Podcast'), (3, 'News'), (4, 'Comment')], help_text="The 'source' or category for this feed", verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='instagram',
            name='username',
            field=models.CharField(help_text='Enter your Instagram username (without @)', max_length=200, unique=True),
        ),
    ]