# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-15 17:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0024_auto_20170613_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='delibera',
            name='pubblicata',
            field=models.BooleanField(default=False, help_text='Se la delibera \xe8 visibile e ricercabile'),
        ),
        migrations.AlterField(
            model_name='delibera',
            name='amministrazioni',
            field=models.ManyToManyField(blank=True, null=True, related_name='delibere', to='delibere.Amministrazione'),
        ),
        migrations.AlterField(
            model_name='delibera',
            name='normative',
            field=models.ManyToManyField(blank=True, null=True, related_name='delibere', to='delibere.Normativa'),
        ),
        migrations.AlterField(
            model_name='delibera',
            name='settori',
            field=models.ManyToManyField(blank=True, null=True, related_name='delibere', to='delibere.Settore'),
        ),
        migrations.AlterField(
            model_name='settore',
            name='display_order',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='settore',
            name='ss_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='settore',
            name='sss_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
