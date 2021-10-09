# Generated by Django 3.2.5 on 2021-07-21 23:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('book_review', '0012_auto_20210722_0248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]