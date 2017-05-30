# coding=utf-8
import os
import requests
import time

from django.core.management.base import BaseCommand, CommandError
import lxml.html

from delibere.models import Delibera, Documento

class Command(BaseCommand):
    """
    Management task to scrape documents and data from the old public website.
    """

    help = 'Scrape documents and data from the old public web site.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year-start',
            dest='year_start',
            default=1967,
            help='Year to start parsing',
        )
        parser.add_argument(
            '--year-end',
            dest='year_end',
            type=int,
            default=int(time.strftime("%Y")) + 1,
            help='Year to end parsing (will parse till the year before this).',
        )
        parser.add_argument(
            '--docs-path',
            dest='docs_path',
            default="./resources/media/docs/",
            help='Relative path to docs directory.',
        )


    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting..."))

        site_url = "http://www.cipecomitato.it"
        base_url = "{0}/it/ricerca_delibere.html".format(site_url)

        # read list of meps
        self.stdout.write(self.style.NOTICE("Scraping delibere from old cipecomitato.it site"))
        for year in range(options['year_start'], options['year_end']):

            self.stdout.write(self.style.NOTICE("Scraping delibere for year {0}".format(year)))
            year_results_html = requests.get(
                "{0}?annoDeliberaSed={1}&comando=Ricerca".format(base_url, year)
            ).content
            self.stdout.write(self.style.NOTICE("{0}?annoDeliberaSed={1}&comando=Ricerca".format(base_url, year)))

            # create docs_path if not existing
            docs_path = "{0}{1}".format(options['docs_path'], year)
            if not os.path.exists(docs_path):
                os.makedirs(docs_path)


            root = lxml.html.fromstring(year_results_html)
            for delibera in root.cssselect("#main-1col tr"):
                if delibera.cssselect("td[class='tabeletxt_ricerca']"):
                    delibera_date = delibera.cssselect(
                        "td[class='tabeletxt_ricerca2']"
                    )[0].text.strip()

                    delibera_numero = delibera.cssselect(
                        "td[class='tabeletxt_ricerca1']"
                    )[0].text.strip().replace('Delibera Num. ', '')
                    delibera_titolo = delibera.cssselect(
                        "td[class='tabeletxt_ricerca1']"
                    )[0].xpath("br")[0].tail.strip()


                    try:
                        delibera_numero_as_int = int(delibera_numero)
                        delibera_id = "{0}{1:03d}".format(year, delibera_numero_as_int)
                    except ValueError:
                        delibera_id = "{0}{1}".format(year, delibera_numero)

                    self.stdout.write(self.style.NOTICE(u"Read delibera {0}".format(delibera_id)))

                    delibera_cc = delibera.cssselect(
                        "td[class='tabeletxt_ricerca']"
                    )[0].text_content().split("\n")
                    if len([i for i in delibera_cc if i.strip() != '']):
                        delibera_cc_data = delibera_cc[2]
                        delibera_cc_registro = delibera_cc[4]
                        delibera_cc_foglio = delibera_cc[6]
                    else:
                        delibera_cc_data = None
                        delibera_cc_registro = None
                        delibera_cc_foglio = None

                    delibera_gu = delibera.cssselect(
                        "td[class='tabeletxt_ricerca']"
                    )[1].text_content().split("\n")
                    if len([i for i in delibera_gu if i.strip() != '']):
                        delibera_gu_data = delibera_gu[2]
                        delibera_gu_numero = delibera_gu[4]
                        delibera_gu_tipologia = delibera_gu[6]
                    else:
                        delibera_gu_data = None
                        delibera_gu_numero = None
                        delibera_gu_tipologia = None

                    # write record out to the sqlite database
                    obj, created = Delibera.objects.update_or_create(
                        id=delibera_id,
                        defaults={
                            "year": year,
                            "date": time.strftime("%Y-%m-%d", time.strptime(delibera_date, "%d/%m/%Y")),
                            "title": delibera_titolo,
                            "number": delibera_numero,
                            "cc_date": time.strftime("%Y-%m-%d", time.strptime(delibera_cc_data, "%d/%m/%Y")) if delibera_cc_data else None,
                            "cc_registro": delibera_cc_registro,
                            "cc_foglio": delibera_cc_foglio,
                            "gu_date": time.strftime("%Y-%m-%d", time.strptime(delibera_gu_data, "%d/%m/%Y")) if delibera_gu_data else None,
                            "gu_numero": delibera_gu_numero,
                            "gu_tipologia": delibera_gu_tipologia,
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS("Delibera {0} created.".format(delibera_id)))
                    else:
                        self.stdout.write(self.style.SUCCESS("Delibera {0} updated".format(delibera_id)))


                    delibera_docs = delibera.cssselect("li a")
                    for doc in delibera_docs:
                        doc_url = "{0}{1}".format(site_url, doc.attrib['href'])
                        doc_name = doc.attrib['href'].split('=')[1]
                        doc_title = doc.text_content().strip()

                        self.stdout.write(self.style.NOTICE("Downloading {0}".format(doc_url)))
                        response = requests.get(doc_url)
                        doc_filename = '{0}/{1}'.format(docs_path, doc_name)
                        with open(doc_filename, 'wb') as f:
                            f.write(response.content)
                        self.stdout.write(self.style.SUCCESS("Saved {0}".format(doc_filename)))

                        # write record out to the sqlite database
                        obj, created = Documento.objects.update_or_create(
                            id=doc_name,
                            defaults={
                                "delibera_id": delibera_id,
                                "name": doc_title,
                                "filepath": doc_filename,
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS("Doc {0} created.".format(doc_name)))
                        else:
                            self.stdout.write(self.style.SUCCESS("Doc {0} updated".format(doc_name)))

        self.stdout.write(self.style.SUCCESS('Successful message'))
