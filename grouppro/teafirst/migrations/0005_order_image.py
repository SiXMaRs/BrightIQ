# Generated by Django 5.1.4 on 2025-02-24 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teafirst', '0004_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='order_images/'),
        ),
    ]
