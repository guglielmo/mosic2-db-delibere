# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-09 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='delibera',
            name='gu_rectification_date',
            field=models.DateField(blank=True, help_text='Data di pubblicazione della rettifica in Gazzetta Ufficiale', max_length=12, null=True, verbose_name='Pub. G.U. - Data'),
        ),
        migrations.AddField(
            model_name='delibera',
            name='gu_rectification_numero',
            field=models.CharField(blank=True, help_text='Numero di pubblicazione della rettifica in Gazzetta Ufficiale', max_length=12, null=True, verbose_name='Pub. G.U. - Numero'),
        ),
        migrations.AddField(
            model_name='delibera',
            name='note',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='delibera',
            name='tipo_delibera',
            field=models.CharField(blank=True, help_text='Il tipo di delibera, se Riparto/Assegnazioni, Altro, Direttive, Piani/Programmi', max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='delibera',
            name='tipo_territorio',
            field=models.CharField(blank=True, help_text='Il tipo di territorio, se Regionale, Nazionale, Miltiregionale, Altro', max_length=32, null=True),
        ),
    ]
