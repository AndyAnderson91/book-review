# Generated by Django 3.2.5 on 2021-07-21 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_review', '0010_alter_book_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='slug',
            field=models.SlugField(max_length=40, null=True),
        ),
    ]
