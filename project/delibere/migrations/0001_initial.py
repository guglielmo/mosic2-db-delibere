# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-09 11:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Delibera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codice', models.CharField(help_text='Codice identificativo anno/seduta.', max_length=7, null=True, unique=True)),
                ('title', models.CharField(help_text='Titolo della delibera', max_length=512, verbose_name='Titolo')),
                ('date', models.DateField(help_text='Data della seduta', max_length=10, verbose_name='Data seduta')),
                ('year', models.CharField(help_text='Anno della seduta', max_length=4, verbose_name='Anno seduta')),
                ('number', models.CharField(help_text="Numero della delibera, per quest'anno", max_length=10, verbose_name='Numero')),
                ('tipo_firmatario', models.CharField(blank=True, help_text='Il tipo di firmatario, se Ministro o altro', max_length=32, null=True)),
                ('cc_date', models.DateField(blank=True, help_text='Data di registrazione presso la Corte dei Conti', max_length=12, null=True, verbose_name='Reg. Corte dei Conti - Data')),
                ('cc_registro', models.CharField(blank=True, help_text='Registro della registrazione presso la Corte dei Conti', max_length=12, null=True, verbose_name='Reg. Corte dei Conti - Registro')),
                ('cc_foglio', models.CharField(blank=True, help_text='Foglio della registrazione presso la Corte dei Conti', max_length=12, null=True, verbose_name='Reg. Corte dei Conti - Foglio')),
                ('gu_date', models.DateField(blank=True, help_text='Data di pubblicazione in Gazzetta Ufficiale', max_length=12, null=True, verbose_name='Pub. G.U. - Data')),
                ('gu_numero', models.CharField(blank=True, help_text='Numero di pubblicazione in Gazzetta Ufficiale', max_length=12, null=True, verbose_name='Pub. G.U. - Numero')),
                ('gu_tipologia', models.CharField(blank=True, help_text='Tipo di pubblicazione in Gazzetta Ufficiale', max_length=12, null=True, verbose_name='Pub. G.U. - Tipologia')),
            ],
            options={
                'db_table': 'delibere_delibera',
                'verbose_name_plural': 'delibere',
            },
        ),
        migrations.CreateModel(
            name='Firmatario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nominativo', models.CharField(help_text='Nominativo del firmatario', max_length=32)),
            ],
            options={
                'verbose_name_plural': 'firmatari',
            },
        ),
        migrations.AddField(
            model_name='delibera',
            name='firmatario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='delibere_firmate', to='delibere.Firmatario'),
        ),
    ]
