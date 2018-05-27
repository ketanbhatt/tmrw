from django.forms import ModelForm
from django_select2.forms import Select2Widget
from suit_redactor.widgets import RedactorWidget


class DayEntryForm(ModelForm):
    class Meta:
        widgets = {
            'day_summary': RedactorWidget(editor_options={}),
            'scrum_summary': RedactorWidget(editor_options={})
        }


class ScrumEntryForm(ModelForm):
    class Meta:
        widgets = {
            'notes': RedactorWidget(editor_options={}),
            'tags': Select2Widget
        }


class JournalEntryForm(ModelForm):
    class Meta:
        widgets = {
            'response': RedactorWidget(editor_options={}),
            'tags': Select2Widget
        }
