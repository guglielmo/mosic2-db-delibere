import os
import string
import sys

import errno
from django.template import loader
from haystack import indexes
from haystack.fields import FacetCharField

import delibere

class DeliberaIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    anno = indexes.IntegerField(model_attr='anno', faceted=True)
    numero = indexes.CharField(model_attr='numero')
    numero_ord = indexes.CharField(indexed=False)
    descrizione = indexes.CharField(model_attr='descrizione', indexed=False)
    seduta_data = indexes.DateTimeField(model_attr='data', faceted=True)
    cc_data = indexes.DateTimeField(model_attr='cc_data', null=True)
    gu_data = indexes.DateTimeField(model_attr='gu_data', null=True)

    tipo_delibera = indexes.CharField(
        stored=False, faceted=True,
        model_attr='tipo_delibera',
        null=True
    )
    firmatario = indexes.CharField(
        stored=False, faceted=True,
        model_attr='firmatario__nominativo',
        null=True
    )
    settori = indexes.MultiValueField(
        stored=False, faceted=True,
        model_attr='settori__descrizione',
        null=True
    )
    amministrazioni = indexes.MultiValueField(
        stored=False, faceted=True,
        model_attr='amministrazioni__denominazione',
        null=True
    )

    def get_model(self):
        return delibere.models.Delibera

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare_numero_ord(self, obj):
        """usa campo numero per ordinamento
        
        vangono aggiunti degli zeri, fino ad avere 4 cifre decimali, in 
        modo che 1, 1b, 10, 11 
        siano ordinati in sequenza e non come 1, 10, 11, 1b.
        """
        num = obj.numero
        return "{0:04d}".format(
            int(num.rstrip(string.punctuation).rstrip(string.letters))
        ) + num.lstrip(string.digits)



    def prepare(self, obj):
        data = super(DeliberaIndex, self).prepare(obj)

        # Due to a library limitation
        # file_obj must have a .name attribute even if you need to set one
        # manually before calling extract_file_contents:
        docs_content = ''
        backend = self._get_backend(None)
        docs = obj.documenti.all()
        for doc in docs:


            if not hasattr(doc, 'file'):
                continue

            # pdf documents from 2009 come from GU and may
            # contain parts of other acts, right before or after
            # the delibera. This would pollute the index, so only the
            # corresponding doc file is indexed.
            # The PDF
            if doc.delibera.anno >= 2009 and \
               doc.file.path.split('.')[-1] == 'pdf':
                continue

            # Only main documents are indexed
            if doc.tipo_documento != 'P':
                continue

            text_path = doc.file.path.replace('docs', 'texts') + '.txt'

            # sys.stdout.write(
            #     u"Indexing: {0}\n".format(text_path)
            # )

            # text content extraction
            try:
                text_data_content = None
                if os.path.exists(text_path):
                    # if text file exists, extract data from there
                    with open(text_path, 'r') as text_obj:
                        text_data_content = text_obj.read()
                else:
                    # proceed to text extraction from document
                    if os.path.exists(doc.file.path) and \
                        doc.file.path.split('.')[-1] in ['doc', 'docx', 'pdf']:
                        with open(doc.file.path, 'rb') as file_obj:
                            extracted_data = backend.extract_file_contents(
                                file_obj, extractFormat='text'
                            )
                        if extracted_data and 'contents' in extracted_data:
                            # strip first and last blank lines
                            text_data_content = extracted_data['contents'].\
                                replace('\n','XXX').\
                                strip('XXX').\
                                replace('XXX', '\n')

                            if doc.file.path.split('.')[-1] == 'doc':
                                text_data_content = "\n".join(
                                    text_data_content.split('\n')[2:]
                                )

                            # save file fore future re-use (cache)
                            if not os.path.exists(os.path.dirname(text_path)):
                                try:
                                    os.makedirs(os.path.dirname(text_path))
                                except OSError as exc: # Guard against race condition
                                    if exc.errno != errno.EEXIST:
                                        raise
                            with open(text_path, 'w') as text_obj:
                                text_obj.write(text_data_content.encode('utf8'))

                # add text content to index
                if text_data_content:
                    docs_content += text_data_content.\
                        replace('\r\n', ' ').replace('\n', '').\
                        strip()
            except Exception as e:
                sys.stderr.write("Errore {0} in {1}".format(e, obj.id))



        # Now we'll finally perform the template processing to render the
        # text field with *all* of our metadata visible for templating:
        t = loader.select_template(
            ('search/indexes/delibere/delibera_text.txt', )
        )
        data['text'] = t.render(
            {
                'object': obj,
                'docs_content': docs_content
            }
         )

        return data
