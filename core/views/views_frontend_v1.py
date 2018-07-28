from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from core.models import DayEntry, TimeLog, ScrumEntry


@login_required
def change_view(request, day_entry_id):
    context = DayEntry.get_scrum_entries(day_entry_id)
    return render(request, 'frontend_v1/index.html', context)


@csrf_exempt
@login_required
def start_timer_view(request, scrum_entry_id):
    TimeLog.start(scrum_entry_id)
    return redirect(request.POST.get('next', '/'))


@csrf_exempt
@login_required
def add_manual_time_view(request, scrum_entry_id):
    TimeLog.add_manual_time(scrum_entry_id, request.POST['minutes'])
    return redirect(request.POST.get('next', '/'))


@csrf_exempt
@login_required
def stop_timer_view(request, scrum_entry_id, time_log_id):
    TimeLog.stop(time_log_id)
    return redirect(request.POST.get('next', '/'))


@csrf_exempt
@login_required
def set_status_view(request, scrum_entry_id):
    ScrumEntry.set_status(scrum_entry_id, request.POST['status'])
    return redirect(request.POST.get('next', '/'))
