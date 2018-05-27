from django.contrib import admin
from suit.admin import SortableStackedInline

from common.admin import CommonAdminMixin
from core.admin_forms import DayEntryForm, ScrumEntryForm, JournalEntryForm
from core.models import DayEntry, JournalEntry, ScrumEntry


class ScrumEntryInline(CommonAdminMixin, SortableStackedInline):
    model = ScrumEntry
    form = ScrumEntryForm
    suit_classes = 'suit-tab suit-tab-scrum'
    sortable = 'order'
    extra = 0

    fields = ['title', 'notes', 'tags', 'final_status', 'created_at', 'soft_delete']


class JournalEntryInline(CommonAdminMixin, SortableStackedInline):
    model = JournalEntry
    form = JournalEntryForm
    suit_classes = 'suit-tab suit-tab-journal'
    sortable = 'order'
    extra = 0

    fields = ['title', 'response', 'tags', 'created_at', 'soft_delete']


class DayEntryAdmin(CommonAdminMixin, admin.ModelAdmin):
    form = DayEntryForm
    inlines = (JournalEntryInline, ScrumEntryInline)

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['record_date', 'time_logged', 'day_summary', 'scrum_summary']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-scrum',),
            'fields': []}),
        (None, {
            'classes': ('suit-tab', 'suit-tab-journal',),
            'fields': []}),
    ]

    suit_form_tabs = (('general', 'General'), ('scrum', 'Scrum'), ('journal', 'Journal'))


admin.site.register(DayEntry, DayEntryAdmin)
