# Generated by Django 3.2.6 on 2021-10-19 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_review', '0051_auto_20210903_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='original_title',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
    ]