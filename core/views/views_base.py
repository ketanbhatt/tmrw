from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.models import DayEntry


@login_required
def day_entry_html(request, day_entry_id):
    context = DayEntry.get_full_context_for_html_render(day_entry_id)
    return render(request, 'day_entry.html', context)
