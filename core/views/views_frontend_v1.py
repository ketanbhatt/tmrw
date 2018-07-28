from django.shortcuts import render

from core.models import DayEntry


def change_view(request, day_entry_id):
    context = DayEntry.get_scrum_entries(day_entry_id)
    return render(request, 'frontend_v1/index.html', context)
