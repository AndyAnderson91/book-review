# Generated by Django 3.2.5 on 2021-08-03 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0030_auto_20210730_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='test1',
            field=models.ImageField(default='img/book_img/default_book.png', upload_to='img/book_img'),
        ),
    ]