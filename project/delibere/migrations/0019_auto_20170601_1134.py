# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-01 11:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0018_auto_20170601_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delibera',
            name='codice',
            field=models.CharField(help_text='Codice identificativo anno/seduta.', max_length=8, null=True, unique=True),
        ),
    ]