from django import forms
from django.contrib import admin

from delibere.models import Firmatario, Delibera, Documento, Amministrazione, \
    Settore, Normativa


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    can_delete = True
    show_change_link = True

class DeliberaAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'descrizione', 'cc_data', 'gu_data')
    fieldsets = (
        (None, {
            'fields': ('id', 'codice', 'descrizione', 'data', 'anno', 'numero',
            'firmatario', 'tipo_firmatario')
        }),
        ('Categorizzazione', {
            'fields': ('tipo_delibera', 'tipo_territorio',
                'amministrazioni', 'normative', 'settori',
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
    search_fields = ('numero', 'anno', 'descrizione')
    inlines = [DocumentoInline,]

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeliberaAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['descrizione'].widget = forms.Textarea(
            attrs={'rows':'5', 'cols': '80'}
        )
        return form


class FirmatarioAdmin(admin.ModelAdmin):
    list_display = ('nominativo',)
    readonly_fields = ('id', )
    search_fields = ('nominativo',)


class AmministrazioneAdmin(admin.ModelAdmin):
    list_display = ('codice', 'denominazione')
    readonly_fields = ('id', )
    search_fields = ('denominazione',)

class SettoreAdmin(admin.ModelAdmin):
    list_display = ('descrizione', 'parent',)
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
