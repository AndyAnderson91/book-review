# Generated by Django 3.2.5 on 2021-07-22 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0015_auto_20210722_0306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='slug',
        ),
    ]
