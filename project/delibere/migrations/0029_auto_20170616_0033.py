# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-16 00:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0028_auto_20170615_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delibera',
            name='amministrazioni',
            field=models.ManyToManyField(blank=True, related_name='delibere', to='delibere.Amministrazione'),
        ),
        migrations.AlterField(
            model_name='delibera',
            name='normative',
            field=models.ManyToManyField(blank=True, related_name='delibere', to='delibere.Normativa'),
        ),
        migrations.AlterField(
            model_name='delibera',
            name='settori',
            field=models.ManyToManyField(blank=True, related_name='delibere', to='delibere.Settore'),
        ),
    ]