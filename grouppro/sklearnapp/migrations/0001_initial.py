# Generated by Django 5.1.4 on 2024-12-24 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SklearnModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('file', models.FileField(blank=True, null=True, upload_to='models/')),
            ],
        ),
    ]
