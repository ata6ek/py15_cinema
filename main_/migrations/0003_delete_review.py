# Generated by Django 4.0 on 2022-01-13 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_', '0002_remove_review_rating'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Review',
        ),
    ]