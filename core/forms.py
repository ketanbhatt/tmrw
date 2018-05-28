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

    def __init__(self, *args, **kwargs):
        super(ScrumEntryForm, self).__init__(*args, **kwargs)
        self.fields['order'].widget.attrs.update({'readonly': 'true'})


class JournalEntryForm(ModelForm):
    class Meta:
        widgets = {
            'response': RedactorWidget(editor_options={}),
        }
