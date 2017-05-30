import hashlib

from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from models import Delibera, Documento


class DocumentoSerializer(serializers.HyperlinkedModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True,
        allow_empty_file=True, read_only=True
    )
    class Meta:
        model = Documento
        fields = ('id', 'filepath', 'name', 'file')


class DeliberaSerializer(serializers.HyperlinkedModelSerializer):
    documenti = DocumentoSerializer(required=False, many=True, write_only=True)
    self_uri = serializers.HyperlinkedIdentityField(view_name = 'delibere-detail')

    def create(self, validated_data):
        """create the Delibera object, all Documento objects
        specified in the data,
        inside an atomic transaction

        :param validated_data: JSON serialized, valid data
        :return: Delibera instance, or None
        """
        seduta = None
        with transaction.atomic():
            documenti_data = []
            if 'documenti' in validated_data:
                documenti_data = validated_data.pop('documenti')

            delibera = Delibera.objects.create(**validated_data)

            for documento_data in documenti_data:
                Documento.objects.create(
                    delibera=delibera, **documento_data
                )

            return delibera

    class Meta:
        model = Delibera
        fields = ('id', 'self_uri', 'date', 'year', 'number', 'title', 'documenti')


class DeliberaDetailSerializer(serializers.HyperlinkedModelSerializer):
    documenti = DocumentoSerializer(required=False, many=True)

    class Meta:
        model = Delibera
        fields = (
            'id','date','year','number', 'title',
            'cc_date', 'cc_registro', 'cc_foglio',
            'gu_date','gu_numero','gu_tipologia',
            'documenti',
        )



