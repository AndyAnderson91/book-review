# Generated by Django 3.2.5 on 2021-07-21 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_review', '0013_alter_review_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(blank=True, max_length=1024),
        ),
    ]