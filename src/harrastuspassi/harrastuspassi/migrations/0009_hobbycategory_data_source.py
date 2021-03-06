# Generated by Django 2.2.4 on 2019-10-10 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harrastuspassi', '0008_hobby_many_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='hobbycategory',
            name='data_source',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='External data source'),
        ),
        migrations.AddField(
            model_name='hobbycategory',
            name='origin_id',
            field=models.CharField(blank=True, default='', max_length=128, verbose_name='ID in external data source'),
        ),
    ]
