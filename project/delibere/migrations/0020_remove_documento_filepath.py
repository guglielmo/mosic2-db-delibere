# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-02 09:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0019_auto_20170601_1134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documento',
            name='filepath',
        ),
    ]