# Generated by Django 3.2.5 on 2021-08-04 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0043_auto_20210804_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='pages',
            field=models.PositiveIntegerField(null=True),
        ),
    ]