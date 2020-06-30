# Generated by Django 2.2.4 on 2020-05-15 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harrastuspassi', '0016_location_created_by_municipality'),
    ]

    operations = [
        migrations.AddField(
            model_name='hobbycategory',
            name='name_en',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='hobbycategory',
            name='name_fi',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='hobbycategory',
            name='name_sv',
            field=models.CharField(max_length=256, null=True),
        ),
    ]