# coding=utf-8
from __future__ import unicode_literals

import os

from django.db import models
from django.urls import reverse

import search_indexes


class Timestampable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=False, null=True)

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
        max_length=8, unique=True, null=True,
        help_text="Codice identificativo anno/seduta."
    )
    slug = models.CharField(
        max_length=14, unique=True, null=True,
        help_text="Slug identificativo numer-data"
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
        max_length=10,
        help_text="Numero della delibera, per quest'anno",
        verbose_name="Numero"
    )

    tipo_delibera = models.CharField(
        max_length=32,
        blank=True, null=True,
        help_text="Il tipo di delibera, se Riparto/Assegnazioni, Altro, Direttive, Piani/Programmi"
    )
    tipo_territorio = models.CharField(
        max_length=32,
        blank=True, null=True,
        help_text="Il tipo di territorio, se Regionale, Nazionale, Miltiregionale, Altro"
    )


    firmatario = models.ForeignKey(
        'Firmatario', on_delete=models.PROTECT, null=True,
        related_name='delibere_firmate', db_constraint=True
    )
    tipo_firmatario = models.CharField(
        max_length=32,
        blank=True, null=True,
        help_text="Il tipo di firmatario, se Ministro o altro"
    )

    amministrazioni = models.ManyToManyField(
        'Amministrazione', related_name='delibere'
    )

    normative = models.ManyToManyField(
        'Normativa', related_name='delibere'
    )

    settori = models.ManyToManyField(
        'Settore', related_name='delibere'
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
        help_text="Tipo di pubblicazione in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Tipologia"
    )

    gu_data_rettifica = models.DateField(
        blank=True, null=True,
        max_length=12,
        help_text="Data di pubblicazione della rettifica in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Data"
    )
    gu_numero_rettifica = models.CharField(
        blank=True, null=True,
        max_length=12,
        help_text="Numero di pubblicazione della rettifica in Gazzetta Ufficiale",
        verbose_name="Pub. G.U. - Numero"
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
        return self.documento_set.filter(
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
        return self.documento_set.filter(
            tipo_documento='P', estensione__iexact='doc'
        )

    @property
    def doc_allegati(self):
        return self.documento_set.filter(tipo_documento='A')

    def __unicode__(self):
        return self.descrizione

    def get_absolute_url(self):
        return reverse('delibera_details', args=[str(self.slug)])

    class Meta:
        db_table = 'delibere_delibera'
        verbose_name_plural = "delibere"

def upload_to(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<relURI>/<filename>
    return '{0}'.format(filename)

class Documento(models.Model):
    # file will contain the file,
    # it is null because it can be added
    # after the Documento object has been created
    file = models.FileField(
        max_length=255,
        blank=True, null=True,
        upload_to=upload_to
    )

    nome = models.CharField(max_length=32, null=True)
    delibera = models.ForeignKey(
        'Delibera',
        null=True,
        related_name='documenti',
        on_delete=models.deletion.CASCADE,
    )
    tipo_documento = models.CharField(
        max_length=1,
        help_text="P - Principale, A - Allegato"
    )
    estensione = models.CharField(
        max_length=4,
        help_text="L'estensione del documento"
    )

    def __unicode__(self):
        return self.file.path


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

    def __unicode__(self):
        return self.denominazione


    class Meta:
        verbose_name_plural = 'amministrazioni'


class Normativa(models.Model):
    descrizione = models.CharField(
        max_length=128,
    )

    def __unicode__(self):
        return self.descrizione


    class Meta:
        verbose_name_plural = 'normative'

class Settore(models.Model):
    parent = models.ForeignKey(
        'self',
        blank=True, null=True,
        related_name='children'
    )
    ss_id = models.IntegerField(
        unique=True, null=True
    )
    sss_id = models.IntegerField(
        unique=True, null=True
    )
    descrizione = models.CharField(
        max_length=128,
    )
    display_order = models.PositiveIntegerField(
        null=True,
    )

    def __unicode__(self):
        return self.descrizione


    class Meta:
        verbose_name_plural = 'settori'

# signals ---------------------------------------------

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Documento)
def documento_post_save_handler(sender, **kwargs):
    """When the documento object is saved
    update data in solr index.

    :param sender:
    :param kwargs:
    :return:
    """
    documento_obj = kwargs['instance']
    index = search_indexes.DeliberaIndex()
    index.update_object(documento_obj.delibera)


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
