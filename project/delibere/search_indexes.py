import os
import sys

import errno
from django.conf import settings
from django.template import loader, Context
from haystack import indexes
from pysolr import SolrError

import delibere

class DeliberaIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    year = indexes.CharField(model_attr='year')
    number = indexes.CharField(model_attr='number')
    title = indexes.CharField(model_attr='title', indexed=False)
    seduta_date = indexes.DateTimeField(model_attr='date')
    cc_date = indexes.DateTimeField(model_attr='cc_date', null=True)
    gu_date = indexes.DateTimeField(model_attr='gu_date', null=True)

    def get_model(self):
        return delibere.models.Delibera

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, obj):
        data = super(DeliberaIndex, self).prepare(obj)

        # This could also be a regular Python open() call, a StringIO instance
        # or the result of opening a URL. Note that due to a library limitation
        # file_obj must have a .name attribute even if you need to set one
        # manually before calling extract_file_contents:
        docs_content = ''
        backend = self._get_backend(None)
        docs = obj.documento_set.all()
        for doc in docs:
            doc_path = os.path.normpath(
                settings.MEDIA_ROOT + '/' +
                doc.filepath
            )
            text_path = doc_path.replace('docs', 'texts') + '.txt'

            # text content extraction
            try:
                text_data_content = None
                if os.path.exists(text_path):
                    # if text file exists, extract data from there
                    with open(text_path, 'r') as text_obj:
                        text_data_content = text_obj.read()
                else:
                    # proceed to text extraction from document
                    if os.path.exists(doc_path) and \
                        doc_path.split('.')[-1] in ['doc', 'docx', 'pdf']:
                        with open(doc_path, 'rb') as file_obj:
                            extracted_data = backend.extract_file_contents(
                                file_obj, extractFormat='text'
                            )
                        if extracted_data and 'contents' in extracted_data:
                            # strip first and last blank lines
                            text_data_content = extracted_data['contents'].\
                                replace('\n','XXX').\
                                strip('XXX').\
                                replace('XXX', '\n')

                            if doc_path.split('.')[-1] == 'doc':
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
            except SolrError as e:
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
