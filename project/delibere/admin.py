from adminsortable2.admin import SortableAdminMixin
from django import forms
from django.contrib import admin
from django.contrib.admin import widgets, SimpleListFilter, FieldListFilter
from django.contrib.admin.utils import reverse_field_path
from mptt.admin import DraggableMPTTAdmin
from mptt.forms import TreeNodeMultipleChoiceField
from django_admin_listfilter_dropdown.filters import DropdownFilter

from delibere.models import Firmatario, Delibera, Documento, Amministrazione, \
    Settore, Normativa


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    can_delete = True
    show_change_link = True
    readonly_fields = ('nome', 'estensione',)


class AnnoDropdownFilter(DropdownFilter):
    """Patch DropdownFilter class to reverse ordering of items in dropdown.

    TODO: It's a hack, a cleaner way should be implemented in the original
        package

    """
    def __init__(self, field, request, params, model, model_admin, field_path):
        super(AnnoDropdownFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

        queryset = model_admin.get_queryset(request)
        self.lookup_choices = (queryset
                               .distinct()
                               .order_by("-{0}".format(field.name))
                               .values_list(field.name, flat=True))


class DataSedutaFilter(SimpleListFilter):

    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Data della seduta'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'data'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        anno = request.GET.get('anno', None)
        items = []
        for item in model_admin.model.objects\
                .filter(anno=anno)\
                .order_by('-data')\
                .values_list('data', flat=True)\
                .distinct():
            items.append((item, item.strftime("%d/%m/%Y")))
        return items

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value():
            return queryset.filter(data=self.value())
        else:
            return queryset

class DeliberaAdmin(admin.ModelAdmin):
    list_display = ('anno', 'data', 'numero', 'descrizione', 'pubblicata')
    list_display_links = ('descrizione',)
    list_filter = (
        ('anno', AnnoDropdownFilter),
        DataSedutaFilter,
    )
    fieldsets = (
        (None, {
            'fields': ('id', 'codice', 'descrizione', 'pubblicata',
                'data', 'anno', 'numero',
                'firmatario',
                'note'
            )
        }),
        ('Categorizzazione', {
            'fields': (
                'amministrazioni', 'settori',
            ),
        }),
        ('Corte dei conti', {
            'fields': ('cc_data', 'cc_registro', 'cc_foglio'),
        }),

        ('Gazzetta Ufficiale', {
            'fields': ('gu_data', 'gu_numero', 'gu_tipologia',
                'gu_data_rettifica', 'gu_numero_rettifica'),
        }),
    )
    readonly_fields = ('id', 'slug', 'created_at', 'updated_at', )
    filter_horizontal = ('amministrazioni', 'settori', )
    search_fields = ('numero', 'anno', 'descrizione')
    ordering = ('-anno', '-numero_ord')
    inlines = [DocumentoInline,]
    save_on_top = True

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeliberaAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['descrizione'].widget = forms.Textarea(
            attrs={'rows':'5', 'cols': '80'}
        )
        form.base_fields['note'].widget = forms.Textarea(
            attrs={'rows':'5', 'cols': '80'}
        )
        form.base_fields['settori'] = TreeNodeMultipleChoiceField(
            required=False,
            queryset=Settore.objects.all()
        )
        form.base_fields['settori'].widget = widgets.FilteredSelectMultiple(
            'Settori',
            False
        )
        form.base_fields['cc_registro'].widget.attrs.update({
            "placeholder": "1",
        })

        return form

class FirmatarioAdmin(admin.ModelAdmin):
    list_display = ('nominativo',)
    readonly_fields = ('id', )
    search_fields = ('nominativo',)


class AmministrazioneAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('codice', 'denominazione',)
    readonly_fields = ('id', )
    search_fields = ('denominazione',)
    list_display_links = ('denominazione',)

class SettoreAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions',
        'indented_title',

    )
    readonly_fields = ('id', 'ss_id', 'sss_id' )
    search_fields = ('descrizione',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(SettoreAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['descrizione'].widget.attrs['style'] = 'width: 45em;'
        return form


class NormativaAdmin(admin.ModelAdmin):
    list_display = ('descrizione',)
    readonly_fields = ('id', )
    search_fields = ('descrizione',)

admin.site.register(Settore, SettoreAdmin)
admin.site.register(Normativa, NormativaAdmin)
admin.site.register(Amministrazione, AmministrazioneAdmin)
admin.site.register(Firmatario, FirmatarioAdmin)
admin.site.register(Delibera, DeliberaAdmin)
