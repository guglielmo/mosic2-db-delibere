import hashlib

from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from models import Delibera, Firmatario, Documento, Settore, Normativa, Amministrazione


class FirmatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firmatario
        fields = ('id', 'nominativo' )

class NormativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Normativa
        fields = ('id', 'descrizione' )


class AmministrazioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amministrazione
        fields = ('id', 'codice', 'denominazione', )


class SettoreSerializer(serializers.ModelSerializer):
    parent = SerializerMethodField(required=False)

    def get_parent(self, obj):
        if obj.parent is not None:
            return SettoreSerializer(obj.parent).data
        else:
            return None

    class Meta:
        model = Settore
        fields = ('id', 'descrizione', 'parent', )

class DocumentoSerializer(serializers.HyperlinkedModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True,
        allow_empty_file=True, read_only=True
    )
    class Meta:
        model = Documento
        fields = ('id', 'nome', 'estensione', 'tipo_documento', 'file')


class DeliberaSerializer(serializers.HyperlinkedModelSerializer):
    documenti = DocumentoSerializer(
        required=False, many=True
    )
    settori = SettoreSerializer(
        required=False, many=True, write_only=True
    )
    firmatario = FirmatarioSerializer(
        required=False, write_only=True
    )
    amministrazioni = AmministrazioneSerializer(
        required=False, many=True, write_only=True
    )
    normative = NormativaSerializer(
        required=False, many=True, write_only=True
    )

    self_uri = serializers.HyperlinkedIdentityField(
        view_name = 'delibere-detail'
    )

    def create(self, validated_data):
        """create the Delibera object and all internal objects
        specified in the data, inside an atomic transaction

        :param validated_data: JSON serialized, valid data
        :return: Delibera instance, or None
        """
        delibera = None
        with transaction.atomic():
            documenti_data = []
            if 'documenti' in validated_data:
                documenti_data = validated_data.pop('documenti')

            settori_data = []
            if 'settori' in validated_data:
                settori_data = validated_data.pop('settori')

            amministrazioni_data = []
            if 'amministrazioni' in validated_data:
                amministrazioni_data = validated_data.pop('amministrazioni')

            normative_data = []
            if 'normative' in validated_data:
                normative_data = validated_data.pop('normative')

            firmatario_data = None
            if 'firmatario' in validated_data:
                firmatario_data = validated_data.pop('firmatario')

            delibera = Delibera.objects.create(**validated_data)

            for documento_data in documenti_data:
                doc_nome = documento_data.pop('nome')
                documento, created = Documento.objects.get_or_create(
                    nome=doc_nome,
                    defaults=documento_data
                )
                delibera.documenti.add(documento)

            for settore_data in settori_data:
                descrizione = settore_data.pop('descrizione')
                settore, created = Settore.objects.get_or_create(
                    descrizione=descrizione,
                    defaults=settore_data
                )
                delibera.settori.add(settore)

            for normativa_data in normative_data:
                descrizione = normativa_data.pop('descrizione')
                normativa, created = Normativa.objects.get_or_create(
                    descrizione=descrizione,
                    defaults=normativa_data
                )
                delibera.normative.add(normativa)

            for amministrazione_data in amministrazioni_data:
                codice = amministrazione_data.pop('codice')
                amministrazione, created = Amministrazione.objects.get_or_create(
                    codice=codice,
                    defaults=amministrazione_data
                )
                delibera.amministrazioni.add(amministrazione)

            if firmatario_data:
                nominativo = firmatario_data.pop('nominativo')
                firmatario, created = Firmatario.objects.get_or_create(
                    nominativo=nominativo,
                    defaults=firmatario_data
                )
                delibera.firmatario = firmatario

            delibera.save()

            return delibera

    class Meta:
        model = Delibera
        fields = (
            'id', 'self_uri',
            'data', 'anno', 'numero', 'descrizione', 'firmatario',
            'documenti', 'settori', 'amministrazioni', 'normative'
        )


class DeliberaDetailSerializer(serializers.HyperlinkedModelSerializer):
    firmatario = FirmatarioSerializer(required=False)
    documenti = DocumentoSerializer(required=False, many=True)
    settori = SettoreSerializer(required=False, many=True)
    amministrazioni = AmministrazioneSerializer(required=False, many=True)
    normative = NormativaSerializer(required=False, many=True)

    class Meta:
        model = Delibera
        fields = (
            'id', 'slug', 'codice',
            'descrizione',
            'tipo_delibera',
            'firmatario', 'tipo_firmatario',
            'data','anno','numero',
            'cc_data', 'cc_registro', 'cc_foglio',
            'gu_data','gu_numero','gu_tipologia',
            'gu_data_rettifica', 'gu_numero_rettifica',
            'documenti',
            'settori', 'amministrazioni', 'normative'
        )



