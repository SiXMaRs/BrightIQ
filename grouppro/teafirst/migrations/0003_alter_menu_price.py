# Generated by Django 5.1.4 on 2025-02-24 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teafirst', '0002_alter_menu_image_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='price',
            field=models.IntegerField(),
        ),
    ]
