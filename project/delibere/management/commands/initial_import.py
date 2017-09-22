# coding=utf-8
import os

import requests
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
import agate
from django.db.models import signals, F
from django.conf import settings

from delibere.models import Delibera, Firmatario, Documento, Amministrazione, \
    Normativa, Settore, documento_post_save_handler

text_type = agate.Text()
number_type = agate.Number()
boolean_type = agate.Boolean()
date_type = agate.Date()
datetime_type = agate.DateTime()


class Command(BaseCommand):
    """
    Management task to import data exported from Oracle into the model
    """

    help = 'Read data from CSV files and import them into the model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--docs-path',
            dest='docs_path',
            default="./resources/fixtures/initial_docs",
            help='Relative path to initial docs files.',
        )
        parser.add_argument(
            '--csv-path',
            dest='csv_path',
            default="./resources/fixtures/initial_csv",
            help='Relative path to initial csv files.',
        )
        parser.add_argument(
            '--tables',
            dest='tables',
            default='all',
            help='Comma-separated list of tables to import (defaults to all)'
        )

    def _anno_from_nomefile(self, nomefile):
        """extract anno from nomefile
        E050125allegati.xls => 2005
        E950139.doc         => 1995

        :param nomefile: nome del file da cui estrarre l'anno
        :return: l'anno nel formato YYYY
        """
        anno = nomefile[1:3]
        if anno[0] > '5':
            anno = '19' + anno
        else:
            anno = '20' + anno
        return anno

    def _import_documenti(self, rows, doc_type):
        """procedura creazione documenti

        :param rows:      le righe del CSV contenente le informazioni
        :param doc_type:  il tipo (documenti, allegati)
        :return:
        """
        self.stdout.write(self.style.NOTICE("Starting import of {0}".format(doc_type)))
        for n, row in enumerate(rows):
            # rel. file path
            file_path = "docs/{0}/{1}".format(
                self._anno_from_nomefile(row['NOMEFILE']),
                row['NOMEFILE']
            )

            # original absolute file path (fixtures)
            original_abs_file_path = os.path.normpath(
                os.path.join(
                    self.docs_path, file_path
                )
            )

            doc, created = Documento.objects.update_or_create(
                nome=row['NOMEFILE'],
                defaults={
                    'delibera_id': row['DELIB_ID'] ,
                    'estensione': row['ESTENSIONE'],
                    'tipo_documento': doc_type[0].upper(),
                }
            )

            try:
                # load content of original file into media
                # simulate a file upload
                if doc.file:
                    storage, path = doc.file.storage, doc.file.path
                    storage.delete(path)

                with open(original_abs_file_path) as fp:
                    doc.file.save(file_path, File(fp), save=True)

            except Exception as e:
                doc_url = \
                    "http://www.cipecomitato.it/it/il_cipe/delibere/" \
                    "download?f={0}".format(row['NOMEFILE'])

                self.stdout.write(self.style.NOTICE(
                    u"Could not find {0} locally. "
                    u"Trying to download from {1}".format(
                        row['NOMEFILE'], doc_url))
                )

                try:
                    response = requests.get(doc_url, timeout=4.0)

                    if doc.file:
                        storage, path = doc.file.storage, doc.file.path
                        storage.delete(path)

                    doc.file.save(file_path, ContentFile(response.content))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        u"Error while importing row with "
                        u"id:{0}. {1}".format(row['ID'], e))
                    )


            if n > 0 and n%500 == 0:
                self.stdout.write(self.style.NOTICE("{0} rows imported on {1}".format(n, len(rows))))

        self.stdout.write(self.style.SUCCESS('Finished'))

    def handle(self, *args, **options):

        tables = options['tables']

        self.docs_path = options['docs_path']
        self.csv_path = options['csv_path']

        self.stdout.write(self.style.NOTICE("Starting..."))

        # disconnect signal (no indexing while importing)
        signals.post_save.disconnect(
            documento_post_save_handler, sender=Documento
        )

        models = [
            'firmatari', 'delibere', 'documenti',
            'amministrazioni', 'normative', 'settori']
        if tables == 'all':
            for m in models:
                getattr(self, 'handle_' + m)()
        else:
            for t in map(str.lower, tables.split(',')):
                if t in models:
                    getattr(self, 'handle_' + t)()

    def handle_firmatari(self):
        self.stdout.write(self.style.NOTICE("Importing firmatari"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_FIRMATARI.csv'.format(
                self.csv_path
            )
        )
        for row in rows:
            Firmatario.objects.update_or_create(
                id=row['ID'],
                defaults={
                    'nominativo': row['DESCRIZIONE']
                }
            )
            self.stdout.write(self.style.NOTICE(u"{ID} - {DESCRIZIONE}".format(**row)))

    def handle_delibere(self):
        self.stdout.write(self.style.NOTICE("Reading delibere file"))

        # Nomi dei campi
        # ID,CODICE,DESCRIZIONE,DATADELIBERA,FIRMA_ID,
        # PUBBLICATA,REGISTRAZIONECDC,DATAREGISTRAZIONECDC,NUMREGISTRO,NUMFOGLIO,
        # PUBBLICAZIONEGU,NUMGU,TIPOPUBBLICAZIONEGU,DATAPUBBLICAZIONEGU,
        # RETTIFICAGU,DATARETTIFICAGU,NUMRETTIFICAGU,
        # NOTE,TIPOFIRMATARIO,TIPODELIBERA,TERRITORIO,DIVISIONE,
        # AREEDEPRESSE,ESTENSORE,DATAORALASTMODIFIED,NUMERO,HIDDEN,DATAORACREAZIONE

        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_DELIBERE.csv'.format(
                self.csv_path
            ),
            column_types=[
                number_type, text_type, text_type, datetime_type, number_type,
                text_type, text_type, datetime_type, text_type, text_type,
                text_type, text_type, text_type, datetime_type,
                text_type, datetime_type, number_type,
                text_type, text_type, text_type, text_type, boolean_type,
                boolean_type, text_type, datetime_type, text_type, boolean_type, datetime_type
            ]
        )

        self.stdout.write(self.style.NOTICE("Starting import of delibere"))
        import locale
        locale.setlocale(locale.LC_TIME, str("it_IT"))
        for n, row in enumerate(rows):
            try:
                Delibera.objects.update_or_create(
                    id=row['ID'],
                    defaults={
                        'slug': "{0}-{1:02d}-{2}-{3}".format(
                            row['CODICE'][3:].lstrip('0'),
                            row['DATADELIBERA'].day,
                            row['DATADELIBERA'].strftime("%B").lower(),
                            row['DATADELIBERA'].year),
                        'codice': row['CODICE'],
                        'descrizione':  row['DESCRIZIONE'],
                        'data': row['DATADELIBERA'],
                        'anno': row['DATADELIBERA'].year,
                        'numero': row['NUMERO'],
                        'firmatario_id': row['FIRMA_ID'],
                        'tipo_firmatario': row['TIPOFIRMATARIO'],
                        'cc_data': row['DATAREGISTRAZIONECDC'],
                        'cc_registro': row['NUMREGISTRO'],
                        'cc_foglio': row['NUMFOGLIO'],
                        'gu_data': row['DATAPUBBLICAZIONEGU'],
                        'gu_numero': row['NUMGU'],
                        'gu_tipologia': row['TIPOPUBBLICAZIONEGU'],
                        'gu_data_rettifica': row['DATARETTIFICAGU'],
                        'gu_numero_rettifica': row['NUMRETTIFICAGU'],
                        'note': row['NOTE'],
                        'tipo_delibera': row['TIPODELIBERA'],
                        'tipo_territorio': row['TERRITORIO'],
                        'created_at': row['DATAORACREAZIONE'],
                        'updated_at': row['DATAORALASTMODIFIED'],
                        # '': row[''],
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    u"Error while importing row with id:{0}. {1}".format(row['ID'], e))
                )
            if n > 0 and n%500 == 0:
                self.stdout.write(self.style.NOTICE(u"{0} rows imported on {1}".format(n, len(rows))))

        self.stdout.write(self.style.SUCCESS('Finished'))

    def handle_documenti(self):
        # Nomi dei campi
        # ID,NOMEFILE,DELIB_ID,ESTENSIONE

        self.stdout.write(self.style.NOTICE("Reading documenti file"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_DOCDELIBERE.csv'.format(
                self.csv_path
            ),
            column_types=[
                number_type, text_type, number_type, text_type
            ]
        )
        self._import_documenti(rows, 'principali')

        self.stdout.write(self.style.NOTICE("Reading allegati file"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_ALLEGATI.csv'.format(
                self.csv_path
            ),
            column_types=[
                number_type, text_type, number_type, text_type
            ]
        )
        self._import_documenti(rows, 'allegati')

    def handle_amministrazioni(self):
        self.stdout.write(self.style.NOTICE("Importing amministrazioni"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_AMMINISTRAZIONI.csv'.format(
                self.csv_path
            )
        )
        for row in rows:
            Amministrazione.objects.update_or_create(
                id=row['ID'],
                defaults={
                    'codice': row['CODICE'],
                    'denominazione': row['DESCRIZIONE']
                }
            )
            self.stdout.write(self.style.NOTICE(u"{ID} - {DESCRIZIONE}".format(**row)))

        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_REL_DELIBERE_AMMIN.csv'.format(
                self.csv_path
            )
        )
        self.stdout.write(self.style.NOTICE("Starting connecting delibere to amministrazioni"))
        for n, row in enumerate(rows):
            delibera = Delibera.objects.get(id=row['DELIB_ID'])
            amministrazione = Amministrazione.objects.get(id=row['AMM_ID'])
            delibera.amministrazioni.add(amministrazione)
            if n > 0 and n%500 == 0:
                self.stdout.write(self.style.NOTICE(u"{0} rows imported on {1}".format(n, len(rows))))

    def handle_normative(self):
        self.stdout.write(self.style.NOTICE("Importing normative"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_NORMATIVE.csv'.format(
                self.csv_path
            )
        )
        for row in rows:
            Normativa.objects.update_or_create(
                id=row['ID'],
                defaults={
                    'descrizione': row['DESCRIZIONE']
                }
            )
            self.stdout.write(self.style.NOTICE(u"{ID} - {DESCRIZIONE}".format(**row)))

        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_REL_DELIBERE_NORMATIVE.csv'.format(
                self.csv_path
            )
        )
        self.stdout.write(self.style.NOTICE("Starting connecting delibere to normative"))
        for n, row in enumerate(rows):
            delibera = Delibera.objects.get(id=row['DELIB_ID'])
            normativa = Normativa.objects.get(id=row['NORMA_ID'])
            delibera.normative.add(normativa)
            if n > 0 and n%500 == 0:
                self.stdout.write(self.style.NOTICE(u"{0} rows imported on {1}".format(n, len(rows))))

    def handle_settori(self):

        # settori di livello 1
        self.stdout.write(self.style.NOTICE("Importing settori"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_SETTORI.csv'.format(
                self.csv_path
            )
        )
        for row in rows:
            Settore.objects.update_or_create(
                id=row['ID'],
                defaults={
                    'descrizione': row['DESCRIZIONE'],
                    'display_order': row['DISPLAYORDER']
                }
            )
            self.stdout.write(self.style.NOTICE(u"{ID} - {DESCRIZIONE}".format(**row)))


        # settori di livello 2
        self.stdout.write(self.style.NOTICE("Importing sottosettori"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_SOTTOSETTORI.csv'.format(
                self.csv_path
            )
        )
        for row in rows:
            Settore.objects.update_or_create(
                ss_id=row['ID'], parent_id=row['SETT_ID'],
                defaults={
                    'descrizione': row['DESCRIZIONE'],
                    'display_order': row['DISPLAYORDER']
                }
            )
            self.stdout.write(self.style.NOTICE(u"{ID} - {DESCRIZIONE}".format(**row)))


        # settori id univoco tra settori e sottosettori
        self.stdout.write(self.style.NOTICE("Connecting delibere to settori"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_SETTORI_SOTTOSETTORI.csv'.format(
                self.csv_path
            )
        )
        for n, row in enumerate(rows):
            if row['SETT_ID'] is not None:
                s = Settore.objects.get(id=row['SETT_ID'])
                s.sss_id = row['ID']
                self.stdout.write(self.style.NOTICE
                    (u"Sottosettore:{SETT_ID} -> SSS:{ID}".format(**row))
                )
            else:
                s = Settore.objects.get(ss_id=row['SS_ID'])
                s.sss_id = row['ID']
                self.stdout.write(self.style.NOTICE
                    (u"Settore:{ID} -> SSS:{ID}".format(**row))
                )
            s.save()

        # connessione delibere-settori
        self.stdout.write(self.style.NOTICE("Connecting delibere to settori"))
        rows = agate.Table.from_csv(
            '{0}/DELIBERECIPE_REL_DELIBERE_SETTORI.csv'.format(
                self.csv_path
            )
        )
        for n, row in enumerate(rows):
            delibera = Delibera.objects.get(id=row['DELIB_ID'])
            try:
                settore = Settore.objects.get(sss_id=row['SSS_ID'])
            except Settore.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    u"Settore con SSS_ID:{SSS_ID} non trovato!".format(**row))
                )

            delibera.settori.add(settore)
            if n > 0 and n%500 == 0:
                self.stdout.write(self.style.NOTICE(
                    u"{0} rows imported on {1}".format(n, len(rows)))
            )

        # aggiustamento delibere con solo sottosettore
        self.stdout.write(self.style.NOTICE(
            "Assigning settore to delibere containing only sottosettore"
        ))
        for d in Delibera.objects.all():
            for s in d.settori.all():
                if s.parent and not s.parent in d.settori.all():
                    self.stdout.write(self.style.NOTICE(
                        u"adding {0} to {1} for {2}".format(
                            s.parent ,s, d
                        )
                    ))
                    d.settori.add(s.parent)

        self.stdout.write(self.style.NOTICE(
            "Removing sottosettori having the same description of settori"
        ))
        Settore.objects.filter(
            parent__isnull=False,
            descrizione__iexact=F('parent__descrizione')
        ).delete()

        self.stdout.write(self.style.NOTICE("Finished"))
