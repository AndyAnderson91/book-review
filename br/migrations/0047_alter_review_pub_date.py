# Generated by Django 3.2.5 on 2021-08-05 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0046_alter_book_original_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='pub_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]