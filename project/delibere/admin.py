from django.contrib import admin

from delibere.models import Firmatario, Delibera, Documento


class DocumentoInline(admin.TabularInline):
    model = Documento
    max_num = 0
    can_delete = False
    show_change_link = True
    readonly_fields = fields = ('filepath', 'nome',)

class DeliberaAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'descrizione', 'cc_data', 'gu_data')
    readonly_fields = ('id', 'numero', 'anno', 'data')
    search_fields = ('',)
    inlines = [DocumentoInline,]

class FirmatarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nominativo')
    readonly_fields = ('id', )
    search_fields = ('nominativo',)


admin.site.register(Firmatario, FirmatarioAdmin)
admin.site.register(Delibera, DeliberaAdmin)
