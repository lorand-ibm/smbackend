# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-20 16:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0069_update_unitaccessibilityshortcomings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='data_source',
            field=models.CharField(max_length=50, null=True),
        ),
    ]