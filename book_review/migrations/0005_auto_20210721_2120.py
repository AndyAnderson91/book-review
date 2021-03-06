# Generated by Django 3.2.5 on 2021-07-21 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_review', '0004_rename_score_review_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='born',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='pub_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='author',
            unique_together={('first_name', 'patronymic', 'last_name', 'born')},
        ),
        migrations.AlterUniqueTogether(
            name='book',
            unique_together={('title', 'pub_date')},
        ),
    ]
