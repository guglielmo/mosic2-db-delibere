#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from collections import OrderedDict

from datetime import datetime
from django.shortcuts import redirect
from django.views.generic import DetailView, TemplateView
from haystack.generic_views import FacetedSearchView
from haystack.query import SearchQuerySet
from rest_framework import viewsets, views, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from forms import DelibereSearchForm, format_facet_field
from models import Delibera, Firmatario, Amministrazione, Settore, Documento


class DelibereSearchView(FacetedSearchView):
    """The view class used to build the search results page
    """

    template_name = "delibere/search.html"
    form_class = DelibereSearchForm
    queryset = SearchQuerySet().order_by('-anno', '-numero_ord')
    facet_fields = [
        'seduta_data', 'anno', 'settori',
        'firmatario', 'amministrazioni',
    ]


    def get(self, request, *args, **kwargs):
        if len(request.GET.keys()) == 0:
            response = redirect('delibere_search')
            response['Location'] += '?q='
            return response
        else:
            return super(DelibereSearchView, self).get(request, *args, **kwargs)


    def _build_facet_field_info(self, field, label, facets_fields=None, field_type='char'):
        """Builds data structure to keep labels and info
        for a given facet section.

        The returned data structure is used in the search_facets.html template
        in order to show the facets, with the links to add or remove filters.

        :param field: faceted field
        :param label: the label used in template
        :param facets_fields: the accepted facet fields,
            if none all are accepted
        :return: the facet data structure
        """
        facet = {}
        facet_counts_fields = self.facets_context.get('fields', {})
        if field in facet_counts_fields:
            facet['label'] = label
            facet['values'] = []
            for c in facet_counts_fields[field]:

                # visible values changed for date fields
                if field_type == 'date':
                    short_label = datetime.strptime(c[0], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%B/%Y")
                else:
                    short_label = c[0]
                if facets_fields is None or c[0] in facets_fields:
                    if c[1] > 0:
                        facet_value = {
                            'key': c[0],
                            'label': c[0],
                            'short_label': short_label,
                            'count': c[1],
                            'urls': self._get_facet_urls(field, c[0]),
                        }
                        facet['values'].append(facet_value)

        return facet

    def _build_range_facet_queries_info(self, name, field, label):
        """Builds data structure to keep labels and info
        for a given range facet section.

        The returned data structure is used in the search_facets.html template
        in order to show the facets, with the links to add or remove filters.

        :param name:  name of the range
        :param field: faceted field
        :param label: the label used in template
        :return: the facet data structure
        """

        facet = {}
        facet_counts_queries = self.facets_context.get('queries', {})
        if name in DelibereSearchForm.RANGES:
            ranges = DelibereSearchForm.RANGES[name]

            facet['label'] = label
            facet['values'] = []
            for range in sorted(ranges.keys()):
                items_count = facet_counts_queries.get(
                    '{}_exact:{}'.format(
                        field, ranges[range]['qrange']
                    )
                )
                if items_count:
                    facet_value = {
                        'key': ranges[range]['qrange'],
                        'label': ranges[range]['label'],
                        'short_label': ranges[range]['label'],
                        'count': items_count,
                        'urls': self._get_facet_urls(field, ranges[range]['qrange']),
                    }
                    facet['values'].append(facet_value)

        return facet

    def _get_facet_urls(self, facet, key):
        """Build and return add_filter and remove_filter urls.
        The urls are used in template, to create actions links.

        :param facet: facet name
        :param key:   facet key (value)
        :return: dictionary containing add_filter and remove_filter urls
        """
        facet_key = u'{}:{}'.format(facet, key)

        params = self.params

        urls = {'add_filter': False, 'remove_filter': False}

        if facet_key in params.getlist('selected_facets'):
            params.getlist('selected_facets').remove(facet_key)
            urls['remove_filter'] = params.urlencode(safe=':')
        else:
            params.getlist('selected_facets').append(facet_key)
            urls['add_filter'] = params.urlencode(safe=':')

        return urls

    @property
    def params(self):
        """QueryString parameters, adjusted and sorted

        - `page` parameter is removed,
        - if `q` is not present, it's inserted, with an empty value,
        - `seected_facets` are sorted before being returned (for consistency)

        :return: a copy of request.GET
        """
        params = self.request.GET.copy()

        if 'q' not in params:
            params['q'] = ''
        if 'page' in params:
            del(params['page'])

        params.setlist('selected_facets', sorted(set(params.getlist('selected_facets'))))

        return params

    def get_context_data(self, **kwargs):
        """This is where the facets and selected facets are inserted
        into the context.

        :param kwargs:
        :return:
        """
        context = super(DelibereSearchView, self).get_context_data(**kwargs)
        context['has_query'] = any(kwargs['form'].data.values())

        params = self.params
        selected_facets = sorted(set(params.getlist('selected_facets')))
        selected_facets_fields = map(lambda i: i.split(':')[0], selected_facets)

        # build nonempty_params dict, to check which parameters
        # were passed by the form
        nonempty_params = {}
        for k, v in params.items():
            if k != 'selected_facets' and v != '':
                nonempty_params[k] = v

        my_facets = OrderedDict()
        self.facets_context = context['facets']

        import locale
        locale.setlocale(locale.LC_TIME, str("it_IT"))

        if 'anno' not in nonempty_params and 'numero' not in nonempty_params:
            my_facets['decennio'] = self._build_range_facet_queries_info(
                'decennio', 'seduta_data', 'Decennio'
            )
        if 'seduta_data' in selected_facets_fields and 'anno' not in nonempty_params:
            my_facets['anno'] = self._build_facet_field_info(
                'anno', "Anno"
            )

        if 'anno' in selected_facets_fields or 'anno' in nonempty_params:
            my_facets['seduta_data'] = self._build_facet_field_info(
                'seduta_data', "Seduta", field_type='date'
            )

        my_facets['settori'] = self._build_facet_field_info(
            'settori', "Settori",
            list(
                Settore.objects.filter(parent__isnull=True).values_list(
                    'descrizione', flat=True).distinct()
                )
        )
        if 'settori' in selected_facets_fields:
            my_facets['sottosettori'] = self._build_facet_field_info(
                'settori', "Sottosettori",
                list(
                    Settore.objects.filter(parent__isnull=False).values_list(
                        'descrizione', flat=True).distinct()
                    )
            )

        my_facets['tipo_delibera'] = self._build_facet_field_info(
            'tipo_delibera', "Tipo di Delibera",
            list(
                Delibera.objects.values_list(
                    'tipo_delibera', flat=True).distinct()
                )
        )
        my_facets['amministrazioni'] = self._build_facet_field_info(
            'amministrazioni', "Amministrazioni",
            list(
                Amministrazione.objects.values_list(
                    'denominazione', flat=True).distinct()
                )
        )
        my_facets['firmatario'] = self._build_facet_field_info(
            'firmatario', "Firmatario",
            list(
                Firmatario.objects.values_list(
                    'nominativo', flat=True).distinct()
                )
        )


        context['my_facets'] = my_facets

        return context

class DeliberaView(DetailView):
    """Vista di dettaglio della delibera"""
    model = Delibera

    def get_context_data(self, **kwargs):
        context = super(DeliberaView, self).get_context_data(**kwargs)

        docs = self.get_object().doc_primari_doc
        if docs.count():
            doc = docs[0]
            text_file = doc.file.path.replace('docs', 'texts').\
                replace('.doc', '.doc.txt').lstrip('.')

            with open(text_file, 'rb') as t:
                context['testo_delibera'] = t.read()

        return context


# ViewSets define the view behavior.

from models import Delibera, Documento
from serializers import DeliberaDetailSerializer, DeliberaSerializer


class DeliberaViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    The DeliberaViewset provides
    `retrieve`, `create`, `list` and `delete` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.

    **create**:
        Creates a new delibera, and all its sub-objects, if they're
        recursively passed in the JSON body

    **list**:
        Lists all delibere. Shows link to detailed views.

    **retrieve**:
        Shows the full details of the delibera identified by `{id}`,
        along with its children objects.

    **delete**:
        Deletes the delibera identified by `{id}` and, recursively,
        its children objects from the Database  and the attached documents from the
        file system.
    """
    queryset = Delibera.objects.all()
    serializer_class = DeliberaSerializer

    def retrieve(self, request, pk=None):
        queryset = Delibera.objects.all()
        delibera = get_object_or_404(queryset, pk=pk)
        serializer = DeliberaDetailSerializer(delibera)
        return Response(serializer.data)



class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, filename):
        """
        Uploads a file.

        The file is put into the `media` path, using part of the hash
        and the `filename` parameter.

        The content of the file is specified in the `file` key of the request
        data.
        """

        # file pointer (content)
        file_ptr = request.data['file']

        # retrieve Documento object, corresponding to file
        try:
            doc_obj = Documento.objects.get(nome=file_ptr.name)

            # remove file from storage if existing, to avoid files duplication
            doc_obj.file.storage.delete(filename)

            # save file to storage
            doc_obj.file.save(filename, file_ptr)

            return Response(
                status=204,
                data={
                    'status': 204,
                    'message':
                        u"File {0} caricato correttamente".format(filename)
                }
            )
        except Documento.DoesNotExist:
            return Response(
                status=404,
                data={
                    'status': 404,
                    'message':
                        u"File {0} non trovato".format(filename)
                }
            )
        except Exception as e:
            return Response(
                status=500,
                data={
                    'status': 500,
                    'message':
                        u"Errore durante caricamento di {0}: {1}".format(filename, repr(e))
                }
            )
