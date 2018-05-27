from django.forms import ModelForm
from suit_redactor.widgets import RedactorWidget


class JournalEntryTemplateForm(ModelForm):
    class Meta:
        widgets = {
            'response': RedactorWidget(editor_options={})
        }


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
        }


class JournalEntryForm(ModelForm):
    class Meta:
        widgets = {
            'response': RedactorWidget(editor_options={}),
        }
