# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-05 17:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('delibere', '0020_remove_documento_filepath'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='normativa',
            options={'verbose_name_plural': 'normative'},
        ),
        migrations.AlterModelOptions(
            name='settore',
            options={'verbose_name_plural': 'settori'},
        ),
        migrations.AlterField(
            model_name='documento',
            name='delibera',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documenti', to='delibere.Delibera'),
        ),
    ]
