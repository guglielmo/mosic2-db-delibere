# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-10 06:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0015_settore_ss_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='settore',
            name='sss_id',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]
