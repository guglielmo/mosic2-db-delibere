# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-16 01:07
from __future__ import unicode_literals

from django.db import migrations

def update_tipo_gu_field(apps, schema_editor):
    # We can't import the Delibere model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Delibera = apps.get_model('delibere', 'Delibera')
    for delibera in Delibera.objects.all():
        if delibera.gu_tipologia == 'ORD':
            delibera.gu_tipologia = 'O'
        elif delibera.gu_tipologia == 'SUP':
            delibera.gu_tipologia = 'S'
        delibera.save()


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0031_auto_20170616_0045'),
    ]

    operations = [
    ]
