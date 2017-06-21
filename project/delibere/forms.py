from datetime import datetime, timedelta
from django import forms
from haystack.forms import FacetedSearchForm

from models import Delibera

format_facet_field = lambda x: '{{!ex={0}_tag}}{0}'.format(x)

class DelibereSearchForm(FacetedSearchForm):

    RANGES = {
        'decennio': {
            '00-2010': {
                'qrange': '[2010-01-01T00:00:00Z TO *]',
                'label': '2010 - oggi',
            },
            '01-2000': {
                'qrange': '[2000-01-01T00:00:00Z TO 2009-12-31T23:59:59Z]',
                'label': '2000 - 2010',
            },
            '02-1990': {
                'qrange': '[1990-01-01T00:00:00Z TO 1999-12-31T23:59:59Z]',
                'label': '1990 - 2000',
            },
            '03-1980': {
                'qrange': '[1980-01-01T00:00:00Z TO 1989-12-31T23:59:59Z]',
                'label': '1980 - 1990',
            },
            '04-1970': {
                'qrange': '[1970-01-01T00:00:00Z TO 1979-12-31T23:59:59Z]',
                'label': '1970 - 1980',
            },
            '05-1960': {
                'qrange': '[1960-01-01T00:00:00Z TO 1969-12-31T23:59:59Z]',
                'label': '1967 - 1970',
            },
        },
    }


    start_seduta_data = forms.DateField(
        required=False, label="dal"
    )
    end_seduta_data = forms.DateField(
        required=False, label="al"
    )

    gu_data = forms.DateField(
        required=False, label="Data pubblicazione in Gazzetta Ufficiale"
    )

    anno = forms.IntegerField(
        required=False, label="Anno",
        min_value=1967, max_value=datetime.now().year,
    )
    numero = forms.CharField(
        required=False, label="Numero",
    )


    def __init__(self, *args, **kwargs):
        super(DelibereSearchForm, self).__init__(*args, **kwargs)

        self.label_suffix = ''
        # customise 'q' field
        self.fields['q'].label = ""
        self.fields['q'].widget.attrs.update({
            "placeholder": "Inserisci un testo da ricercare all'interno delle delibere",
            "class": "form-control"
        })
        anno_choices = [('','----')] + [
            (x,str(x)) for x in range(datetime.now().year, 1967, -1)
        ]
        self.fields['anno'] = forms.ChoiceField(
            choices = anno_choices, required=False
        )


    def search(self):
        if not self.cleaned_data.get('q'):
            sqs = self.searchqueryset.all()
        else:
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        for k,v in self.RANGES['decennio'].items():
            sqs = sqs.query_facet(
                'seduta_data',
                v['qrange']
            )

        if not self.is_valid():
            return self.no_query_found()


        if self.cleaned_data['anno']:
            self.selected_facets.append('anno:{0}'.format(self.cleaned_data['anno']))

        # We need to process each facet to ensure that the field name and the
        # value are quoted correctly and separately:
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if value:
                if any(map(lambda x: x in value, ['[', ']', 'TO'])):
                    # ranged queries
                    sqs = sqs.narrow(u'%s:%s' % (field, value))
                else:
                    # non-ranged queries
                    sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

        # Check to see if a start_date was chosen.
        if self.cleaned_data['start_seduta_data']:
            sqs = sqs.filter(seduta_data__gte=self.cleaned_data['start_seduta_data'])

        # Check to see if an end_date was chosen.
        if self.cleaned_data['end_seduta_data']:
            sqs = sqs.filter(seduta_data__lte=self.cleaned_data['end_seduta_data'])

        # Check to see if an end_date was chosen.
        if self.cleaned_data['gu_data']:
            sqs = sqs.filter(
                gu_data__lte=self.cleaned_data['gu_data'] + timedelta(days=1),
                gu_data__gte=self.cleaned_data['gu_data']
            )

        if self.cleaned_data['numero']:
            sqs = sqs.filter(numero=self.cleaned_data['numero'])

        return sqs.load_all()
