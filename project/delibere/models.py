# coding=utf-8
from __future__ import unicode_literals

import locale
import os
import string

from datetime import datetime
from django.db import models
from django.urls import reverse
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

import search_indexes


class Timestampable(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, null=True,
        verbose_name="Data di creazione"
    )
    updated_at = models.DateTimeField(
        auto_now=False, null=True,
        verbose_name="Data di modifica"
    )

    class Meta:
        abstract = True


class Firmatario(models.Model):
    nominativo = models.CharField(
        max_length=32,
        help_text="Nominativo del firmatario",
    )
    def __unicode__(self):
        return self.nominativo

    class Meta:
        verbose_name_plural = "firmatari"


class Delibera(Timestampable, models.Model):
    codice = models.CharField(
        max_length=8, unique=True,
        help_text="Codice identificativo anno/seduta."
    )
    slug = models.CharField(
        max_length=32, unique=True, null=True,
        verbose_name="Identificativo nella URL",
        help_text="Slug identificativo numero-data"
    )
    pubblicata = models.BooleanField(
        default=False,
        help_text="Se la delibera è visibile e ricercabile"
    )
    descrizione = models.CharField(
        max_length=512,
        help_text="Titolo della delibera",
        verbose_name="Titolo"
    )
    data = models.DateField(
        max_length=10,
        help_text="Data della seduta",
        verbose_name="Data seduta"
    )
    anno = models.CharField(
        max_length=4,
        help_text="Anno della seduta",
        verbose_name="Anno seduta"
    )
    numero = models.CharField(
        max_length=16,
        help_text="Numero della delibera, per quest'anno",
        verbose_name="Numero"
    )
    numero_ord = models.CharField(
        max_length=16,
        null=True, blank=True,
        help_text="Numero della delibera, adatto per l'ordinamento",
        verbose_name="Numero"
    )

    tipo_delibera = models.CharField(
        max_length=32,
        blank=True, null=True,
        choices=(
            ('Riparto/Assegnazioni', 'Riparto/Assegnazioni'),
            ('Direttive', 'Direttive'),
            ('Piani/Programmi', 'Piani/Programmi'),
            ('Altro', 'Altro'),
        )
    )
    tipo_territorio = models.CharField(
        max_length=32,
        blank=True, null=True,
        choices=(
            ('Regionale', 'Regionale'),
            ('Nazionale', 'Nazionale'),
            ('Multiregionale', 'Multiregionale'),
            ('Altro', 'Altro'),
        )
    )


    firmatario = models.ForeignKey(
        'Firmatario', on_delete=models.PROTECT, null=True,
        related_name='delibere_firmate', db_constraint=True
    )
    tipo_firmatario = models.CharField(
        max_length=32,
        blank=True, null=True,
        choices=(
            ('Ministro', 'Ministro'),
            ('Altro', 'Altro')
        )
    )

    amministrazioni = models.ManyToManyField(
        'Amministrazione', related_name='delibere',
        blank=True,
    )

    normative = models.ManyToManyField(
        'Normativa', related_name='delibere',
        blank=True,
    )

    settori = models.ManyToManyField(
        'Settore', related_name='delibere',
        blank=True,
    )

    cc_data = models.DateField(
        blank=True, null=True,
        max_length=12,
        help_text="Data di registrazione presso la Corte dei Conti",
        verbose_name="Reg. Corte dei Conti - Data"
    )
    cc_registro = models.CharField(
        blank=True, null=True,
        max_length=12,
        help_text="Registro della registrazione presso la Corte dei Conti",
        verbose_name="Reg. Corte dei Conti - Registro"
    )
    cc_foglio = models.CharField(
        blank=True, null=True,
        max_length=12,
        help_text="Foglio della registrazione presso la Corte dei Conti",
        verbose_name="Reg. Corte dei Conti - Foglio"
    )

    gu_data = models.DateField(
        blank=True, null=True,
        max_length=12,
        help_text="Data di pubblicazione in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Data"
    )
    gu_numero = models.CharField(
        blank=True, null=True,
        max_length=12,
        help_text="Numero di pubblicazione in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Numero"
    )
    gu_tipologia = models.CharField(
        blank=True, null=True,
        max_length=12,
        choices=(
            ('O', 'Ordinaria'),
            ('S', 'Supplemento'),
            ('I', 'Inserzioni?'),

        ),
        help_text="Tipo di pubblicazione in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Tipologia"
    )

    gu_data_rettifica = models.DateField(
        blank=True, null=True,
        max_length=12,
        help_text="Data di pubblicazione della rettifica in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Data rettifica"
    )
    gu_numero_rettifica = models.CharField(
        blank=True, null=True,
        max_length=12,
        help_text="Numero di pubblicazione della rettifica in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Numero rettifica"
    )

    note = models.CharField(
        max_length=512,
        blank=True, null=True
    )


    @property
    def settoriprimari(self):
        return self.settori.filter(parent__isnull=True)

    @property
    def sottosettori(self):
        return self.settori.filter(parent__isnull=False)

    @property
    def doc_primari_pdf(self):
        return self.documenti.filter(
            tipo_documento='P', estensione__iexact='pdf'
        )


    @property
    def doc_primario(self):
        if self.doc_primari_pdf.count():
            return self.doc_primari_pdf[0]
        elif self.doc_primari_doc.count():
            return self.doc_primari_doc[0]
        else:
            return None


    @property
    def doc_primari_doc(self):
        return self.documenti.filter(
            tipo_documento='P', estensione__iexact='doc'
        )

    @property
    def doc_allegati(self):
        return self.documenti.filter(
            tipo_documento='A'
        )

    @property
    def doc_allegati_visibili(self):
        return self.doc_allegati.filter(
            visibilita_allegati=True
        )

    def __unicode__(self):
        return self.descrizione

    def get_absolute_url(self):
        return reverse('delibera_details', args=[str(self.slug)])

    class Meta:
        db_table = 'delibere_delibera'
        verbose_name_plural = "delibere"

def upload_to(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<relURI>/<filename>
    anno = instance.delibera.anno
    return 'docs/{0}/{1}'.format(anno, filename)

class Documento(models.Model):
    # file will contain the file,
    # it is null because it can be added
    # after the Documento object has been created
    file = models.FileField(
        max_length=255,
        blank=True, null=True,
        upload_to=upload_to
    )

    nome = models.CharField(
        max_length=32,
        null=True, blank=True,
        unique=True
    )
    delibera = models.ForeignKey(
        'Delibera',
        null=True,
        related_name='documenti',
        on_delete=models.deletion.CASCADE,
    )
    tipo_documento = models.CharField(
        max_length=1,
        choices=(
            ('P', 'Principale'),
            ('A', 'Allegato')
        )
    )
    estensione = models.CharField(
        max_length=4,
        blank=True, null=True,
        help_text="L'estensione del documento (doc, docx, pdf, ppt, xls, ...)"
    )
    visibilita_allegati = models.BooleanField(
        'Visibilità allegato',
        default=True,
        help_text="Marcare la casella per rendere un allegato non visibile"
    )

    def __unicode__(self):
        if self.file:
            return self.file.path
        else:
            return self.nome


    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documenti'


class Amministrazione(models.Model):
    codice = models.CharField(
        max_length=5,
        blank=True, null=True
    )
    denominazione = models.CharField(
        max_length=128,
    )
    posizione = models.PositiveIntegerField(
        default=0, blank=False, null=False
    )

    def __unicode__(self):
        return self.denominazione


    class Meta:
        ordering = ('posizione',)
        verbose_name_plural = 'amministrazioni'


class Normativa(models.Model):
    descrizione = models.CharField(
        max_length=128,
    )

    def __unicode__(self):
        return self.descrizione


    class Meta:
        verbose_name_plural = 'normative'


class Settore(MPTTModel):
    parent = TreeForeignKey(
        'self',
        blank=True, null=True,
        related_name='children',
        db_index=True
    )
    ss_id = models.IntegerField(
        unique=True, null=True, blank=True
    )
    sss_id = models.IntegerField(
        unique=True, null=True, blank=True
    )
    descrizione = models.CharField(
        max_length=128,
    )
    display_order = models.PositiveIntegerField(
        null=True, blank=True
    )

    def __unicode__(self):
        return self.descrizione


    class Meta:
        verbose_name_plural = 'settori'



# signals ---------------------------------------------

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Delibera)
def delibera_post_save_handler(sender, **kwargs):
    """When the delibera object is saved,
    update data in solr index.

    :param sender:
    :param kwargs:
    :return:
    """
    post_save.disconnect(delibera_post_save_handler, sender=sender)

    delibera_obj = kwargs['instance']

    # overwrite slug
    locale.setlocale(locale.LC_TIME, str("it_IT"))
    delibera_obj.slug = "{0}-{1:02d}-{2}-{3}".format(
        delibera_obj.codice[3:].lstrip('0'),
        delibera_obj.data.day,
        delibera_obj.data.strftime("%B").lower(),
        delibera_obj.data.year
    )

    # overwrite numero_ord
    num = delibera_obj.numero
    delibera_obj.numero_ord =  "{0:04d}".format(
        int(num.rstrip(string.punctuation).rstrip(string.letters))
    ) + num.lstrip(string.digits)

    # defaults if not set
    if delibera_obj.cc_data is not None and delibera_obj.cc_registro == '':
        delibera_obj.cc_registro = 1

    delibera_obj.save()

    index = search_indexes.DeliberaIndex()
    if delibera_obj.pubblicata:
        index.update_object(delibera_obj)
    else:
        index.remove_object(delibera_obj)

    post_save.connect(delibera_post_save_handler, sender=sender)


@receiver(post_delete, sender=Delibera)
def delibera_post_delete_handler(sender, **kwargs):
    """When the delibera object is removed
    remove data from solr index,

    :param sender:
    :param kwargs:
    :return:
    """
    delibera_obj = kwargs['instance']
    index = search_indexes.DeliberaIndex()
    index.remove_object(delibera_obj)



@receiver(post_save, sender=Documento)
def documento_post_save_handler(sender, **kwargs):
    """When the documento object is saved
    update all delibera data in solr index.

    :param sender:
    :param kwargs:
    :return:
    """
    documento_obj = kwargs['instance']

    post_save.disconnect(documento_post_save_handler, sender=sender)

    # nome and estensione can be retrieved from the file object
    if documento_obj.nome is None:
        documento_obj.nome = documento_obj.file.name.split('/')[-1]
    documento_obj.estensione = documento_obj.nome.split('.')[-1]
    documento_obj.save()

    index = search_indexes.DeliberaIndex()
    if documento_obj.delibera and documento_obj.delibera.pubblicata:
        index.update_object(documento_obj.delibera)

    post_save.connect(documento_post_save_handler, sender=sender)


@receiver(post_delete, sender=Documento)
def documento_post_delete_handler(sender, **kwargs):
    """When the allegato object is removed
    remove files from storage.

    :param sender:
    :param kwargs:
    :return:
    """
    documento_obj = kwargs['instance']
    if documento_obj.file:
        storage, path = documento_obj.file.storage, documento_obj.file.path
        storage.delete(path)

        # remove extracted text document if it exists
        text_path = documento_obj.file.path.replace('docs', 'texts') + '.txt'
        if os.path.exists(text_path):
            os.remove(text_path)
