#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ViewSets define the view behavior.
from collections import OrderedDict

from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import viewsets, views, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

# from models import Delibera, Documento
# from serializers import DeliberaDetailSerializer, DeliberaSerializer
    
# class DeliberaViewSet(mixins.CreateModelMixin,
#                       mixins.ListModelMixin,
#                       mixins.RetrieveModelMixin,
#                       mixins.DestroyModelMixin,
#                       viewsets.GenericViewSet):
#     """
#     The DeliberaViewset provides
#     `retrieve`, `create`, `list` and `delete` actions.
#
#     To use it, override the class and set the `.queryset` and
#     `.serializer_class` attributes.
#
#     create:
#     Creates a new delibera, and all its sub-objects, if they're
#     recursively passed in the JSON body
#
#     list:
#     Lists all delibere. Shows link to detailed views.
#
#     retrieve:
#     Shows the full details of the delibera identified by `{id}`,
#     along with its children objects.
#
#     delete:
#     Deletes the delibera identified by `{id}` and, recursively,
#     its children objects from the Database  and the attached documents from the
#     file system.
#     """
#     queryset = Delibera.objects.all()
#     serializer_class = DeliberaSerializer
#
#     def retrieve(self, request, pk=None):
#         queryset = Delibera.objects.all()
#         seduta = get_object_or_404(queryset, pk=pk)
#         serializer = DeliberaDetailSerializer(seduta)
#         return Response(serializer.data)
#
#
#
# class FileUploadView(views.APIView):
#     parser_classes = (FileUploadParser,)
#
#     def put(self, request, filename):
#         """
#         Uploads a file.
#
#         The file is put into the `media` path, using part of the hash
#         and the `filename` parameter.
#
#         The content of the file is specified in the `file` key of the request
#         data.
#         """
#
#         # file pointer (content)
#         file_ptr = request.data['file']
#
#         # retrieve Allegato object, corresponding to file
#         try:
#             documento_obj = Documento.objects.get(filepath=filename)
#
#             complete_filename = "{0}".format(
#                 filename
#             )
#
#             # remove file from storage if existing, to avoid files duplication
#             documento_obj.file.storage.delete(complete_filename)
#
#             # save file to storage
#             documento_obj.file.save(complete_filename, file_ptr)
#
#             return Response(
#                 status=204,
#                 data={
#                     'status': 204,
#                     'message':
#                         u"File {0} caricato correttamente".format(filename)
#                 }
#             )
#         except Documento.DoesNotExist:
#             return Response(
#                 status=404,
#                 data={
#                     'status': 404,
#                     'message':
#                         u"File {0} non trovato".format(filename)
#                 }
#             )
#         except Exception as e:
#             return Response(
#                 status=500,
#                 data={
#                     'status': 500,
#                     'message':
#                         u"Errore durante caricamento di {0}: {1}".format(filename, repr(e))
#                 }
#             )
