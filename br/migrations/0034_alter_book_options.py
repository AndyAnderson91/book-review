# Generated by Django 3.2.5 on 2021-08-03 22:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0033_alter_book_img'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title']},
        ),
    ]
