from itertools import groupby
from operator import itemgetter

from django.forms import BaseInlineFormSet

from core.models import RepeatingScrumEntry, JournalEntryTemplate


class ScrumEntryInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs['instance'].pk is None:
            initial = kwargs.get('initial', [])
            initial += self.get_initial()
            kwargs['initial'] = initial

        super(ScrumEntryInlineFormSet, self).__init__(*args, **kwargs)

    def get_initial(self):
        entries = RepeatingScrumEntry.active_qs().values('title', 'tags')
        initial = []

        for title, group in groupby(entries, itemgetter('title')):
            initial.append({
                'title': title,
                'tags': [row['tags'] for row in group]
            })

        return initial


class JournalEntryInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs['instance'].pk is None:
            initial = kwargs.get('initial', [])
            initial += self.get_initial()
            kwargs['initial'] = initial

        super(JournalEntryInlineFormSet, self).__init__(*args, **kwargs)

    def get_initial(self):
        entries = JournalEntryTemplate.active_qs().values('title', 'response', 'tags')
        initial = []

        for title, group in groupby(entries, itemgetter('title')):
            group = list(group)

            initial.append({
                'title': title,
                'response': group[0]['response'],
                'tags': [row['tags'] for row in group]
            })

        return initial
