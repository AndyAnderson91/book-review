# Generated by Django 3.2.5 on 2021-08-03 23:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book_review', '0036_auto_20210804_0231'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='short_img',
            new_name='small_img',
        ),
    ]