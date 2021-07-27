# Generated by Django 3.2.5 on 2021-07-26 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0022_alter_genre_plural_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='slug',
            field=models.SlugField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='genre',
            name='slug',
            field=models.SlugField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='slug',
            field=models.SlugField(max_length=80),
        ),
    ]