from django.contrib import admin
from nested_admin.nested import NestedStackedInline, NestedModelAdmin, NestedTabularInline
from suit.admin import SortableStackedInline

from common.admin import CommonAdminMixin
from common.utils import get_humanised_time_str
from core.forms import DayEntryForm, ScrumEntryForm, JournalEntryForm, JournalEntryTemplateForm
from core.formsets import ScrumEntryInlineFormSet, JournalEntryInlineFormSet
from core.models import DayEntry, JournalEntry, ScrumEntry, Tag, DayEntryTagStat, JournalEntryTemplate, \
    RepeatingScrumEntry, TimeLog


class RepeatingScrumEntryAdmin(CommonAdminMixin, admin.ModelAdmin):
    readonly_fields = CommonAdminMixin.common_readonly
    list_display = ('title',)
    autocomplete_fields = ['tags']


class JournalEntryTemplateAdmin(CommonAdminMixin, admin.ModelAdmin):
    form = JournalEntryTemplateForm

    readonly_fields = CommonAdminMixin.common_readonly
    list_display = ('title',)
    autocomplete_fields = ['tags']


class TimeLogNestedInline(CommonAdminMixin, NestedTabularInline):
    model = TimeLog
    fields = ('soft_delete', 'start_time', 'end_time', 'duration')
    extra = 1


class ScrumEntryInline(CommonAdminMixin, NestedStackedInline):
    model = ScrumEntry
    form = ScrumEntryForm
    formset = ScrumEntryInlineFormSet

    suit_classes = 'suit-tab suit-tab-scrum'
    sortable_field_name = 'order'

    fields = ['title', 'notes', 'tags', 'final_status', 'created_at', 'soft_delete', 'order']
    readonly_fields = CommonAdminMixin.common_readonly
    autocomplete_fields = ['tags']

    inlines = (TimeLogNestedInline,)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return RepeatingScrumEntry.active_qs().count() + 1
        else:
            return 1

    def get_queryset(self, request):
        qs = super(ScrumEntryInline, self).get_queryset(request)
        return qs.order_by('order')


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

    fields = ('tag', 'time_logged_str')
    readonly_fields = ('tag', 'time_logged_str')

    def has_add_permission(self, request):
        return False

    def time_logged_str(self, obj):
        return get_humanised_time_str(obj.time_logged)
    time_logged_str.short_description = "Time Logged"


class DayEntryAdmin(CommonAdminMixin, NestedModelAdmin):
    form = DayEntryForm
    inlines = (JournalEntryInline, ScrumEntryInline, DayEntryTagStatInline)
    ordering = ('record_date',)

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': ['record_date', 'time_logged_str', 'tags']
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-scrum',),
            'fields': ['scrum_summary']}),
        (None, {
            'classes': ('suit-tab', 'suit-tab-journal',),
            'fields': ['day_summary']}),
    ]

    suit_form_tabs = (('general', 'General'), ('scrum', 'Scrum'), ('journal', 'Journal'))
    readonly_fields = ('time_logged_str',) + CommonAdminMixin.common_readonly
    autocomplete_fields = ['tags']
    change_form_template = 'admin/dayentry/change_form.html'

    def save_related(self, request, form, formsets, change):
        super(DayEntryAdmin, self).save_related(request, form, formsets, change)

        if form.instance.id:
            DayEntry.update_time_logged_for_day(form.instance.id)

    def time_logged_str(self, obj):
        return get_humanised_time_str(obj.time_logged)
    time_logged_str.short_description = "Time Logged"


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
