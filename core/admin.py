from django.contrib import admin
from suit.admin import SortableStackedInline

from common.admin import CommonAdminMixin
from core.forms import DayEntryForm, ScrumEntryForm, JournalEntryForm, JournalEntryTemplateForm
from core.formsets import ScrumEntryInlineFormSet, JournalEntryInlineFormSet
from core.models import DayEntry, JournalEntry, ScrumEntry, Tag, DayEntryTagStat, JournalEntryTemplate, \
    RepeatingScrumEntry


class RepeatingScrumEntryAdmin(CommonAdminMixin, admin.ModelAdmin):
    readonly_fields = CommonAdminMixin.common_readonly
    list_display = ('title',)
    autocomplete_fields = ['tags']


class JournalEntryTemplateAdmin(CommonAdminMixin, admin.ModelAdmin):
    form = JournalEntryTemplateForm

    readonly_fields = CommonAdminMixin.common_readonly
    list_display = ('title',)
    autocomplete_fields = ['tags']


class ScrumEntryInline(CommonAdminMixin, SortableStackedInline):
    model = ScrumEntry
    form = ScrumEntryForm
    formset = ScrumEntryInlineFormSet

    suit_classes = 'suit-tab suit-tab-scrum'
    sortable = 'order'

    fields = ['title', 'notes', 'tags', 'final_status', 'created_at', 'soft_delete']
    readonly_fields = CommonAdminMixin.common_readonly
    autocomplete_fields = ['tags']

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return RepeatingScrumEntry.active_qs().count() + 1
        else:
            return 1


class JournalEntryInline(CommonAdminMixin, SortableStackedInline):
    model = JournalEntry
    form = JournalEntryForm
    formset = JournalEntryInlineFormSet

    suit_classes = 'suit-tab suit-tab-journal'
    sortable = 'order'
    extra = 0

    fields = ['title', 'response', 'tags', 'created_at', 'soft_delete']
    readonly_fields = CommonAdminMixin.common_readonly
    autocomplete_fields = ['tags']

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return JournalEntryTemplate.active_qs().count() + 1
        else:
            return 1


class DayEntryTagStatInline(CommonAdminMixin, admin.TabularInline):
    model = DayEntryTagStat
    suit_classes = 'suit-tab suit-tab-general'
    extra = 0

    def has_add_permission(self, request):
        return False


class DayEntryAdmin(CommonAdminMixin, admin.ModelAdmin):
    form = DayEntryForm
    inlines = (JournalEntryInline, ScrumEntryInline, DayEntryTagStatInline)
    ordering = ('record_date',)

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['record_date', 'time_logged', 'tags']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-scrum',),
            'fields': ['scrum_summary']}),
        (None, {
            'classes': ('suit-tab', 'suit-tab-journal',),
            'fields': ['day_summary']}),
    ]

    suit_form_tabs = (('general', 'General'), ('scrum', 'Scrum'), ('journal', 'Journal'))
    readonly_fields = ('time_logged',) + CommonAdminMixin.common_readonly
    autocomplete_fields = ['tags']


class TagAdmin(CommonAdminMixin, admin.ModelAdmin):
    search_fields = ['name']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(TagAdmin, self).get_readonly_fields(request, obj) + CommonAdminMixin.common_readonly
        if obj is not None:
            readonly_fields = ('name',) + readonly_fields
        return readonly_fields


admin.site.register(DayEntry, DayEntryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(JournalEntryTemplate, JournalEntryTemplateAdmin)
admin.site.register(RepeatingScrumEntry, RepeatingScrumEntryAdmin)
