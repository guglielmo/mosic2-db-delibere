# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-09 14:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0003_auto_20170509_1637'),
    ]

    operations = [
        migrations.RenameField(
            model_name='delibera',
            old_name='year',
            new_name='anno',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='cc_date',
            new_name='cc_data',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='date',
            new_name='data',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='title',
            new_name='descrizione',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='gu_date',
            new_name='gu_data',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='gu_rectification_date',
            new_name='gu_data_rettifica',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='gu_rectification_numero',
            new_name='gu_numero_rettifica',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='notes',
            new_name='note',
        ),
        migrations.RenameField(
            model_name='delibera',
            old_name='number',
            new_name='numero',
        ),
    ]
