import datetime
from collections import defaultdict

from bulk_update.helper import bulk_update
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import Prefetch
from django.utils.safestring import mark_safe

from common.models import CommonInfoAbstractModel
from common.utils import get_humanised_time_str


class Tag(CommonInfoAbstractModel):
    name = models.SlugField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class DayEntry(CommonInfoAbstractModel):
    record_date = models.DateField(default=datetime.date.today, unique=True, help_text="Date of the DayEntry")
    day_summary = models.TextField(null=True, blank=True, help_text="Summary for the day")
    scrum_summary = models.TextField(null=True, blank=True, help_text="Summary for the *Work* day")
    time_logged = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MaxValueValidator(60*24, message="You can't log more than 24 hours in a day")],
        help_text="Total time logged in the day in minutes"
    )
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name_plural = 'Day Entries'

    def __str__(self):
        return "DayEntry: {}".format(self.record_date)

    @classmethod
    def update_time_logged_for_day(cls, day_entry_id):
        time_logged, tagged_time = cls.get_total_and_tagged_time(day_entry_id)

        cls.objects.filter(id=day_entry_id).update(time_logged=time_logged)

        if tagged_time:
            DayEntryTagStat.create_tag_stats_for_day_entry(day_entry_id, tagged_time)

    @classmethod
    def get_total_and_tagged_time(cls, day_entry_id):
        day_entry = cls.objects.prefetch_related(
            Prefetch(
                'scrumentry_set',
                queryset=ScrumEntry.active_qs().prefetch_related('tags').prefetch_related(
                    Prefetch('timelog_set', TimeLog.active_qs().filter(duration__isnull=False), to_attr='time_logs'),
                ),
                to_attr='scrum_entries'
            )
        ).get(id=day_entry_id)

        total_time, tagged_time = 0, defaultdict(int)
        for scrum_entry in day_entry.scrum_entries:
            logged_time = sum([log.duration for log in scrum_entry.time_logs])

            for tag in scrum_entry.tags.all():
                tagged_time[tag.id] += logged_time
            total_time += logged_time

        return total_time, tagged_time

    @classmethod
    def get_scrum_entries(cls, day_entry_id):
        scrum_entries = []
        day_entry = cls.objects.prefetch_related(
            Prefetch(
                'scrumentry_set',
                queryset=ScrumEntry.active_qs().order_by('order').prefetch_related(
                    Prefetch('timelog_set', TimeLog.active_qs(), to_attr='time_logs'),
                ),
                to_attr='scrum_entries'
            )
        ).get(id=day_entry_id)

        for scrum_entry in day_entry.scrum_entries:
            kwargs = {
                "id": scrum_entry.id,
                "title": scrum_entry.title,
                "final_status": ScrumEntry.FINAL_STATUS_CHOICES_DICT[scrum_entry.final_status],
                "final_status_classes": ScrumEntry.FINAL_STATUS_BOOTSTRAP_CLASSES[scrum_entry.final_status],
            }

            total_time_logged, ongoing_time, ongoing_time_log_id = 0, None, None
            for time_log in scrum_entry.time_logs:
                if time_log.duration:
                    total_time_logged += time_log.duration
                else:
                    now, start_time = datetime.datetime.now(), time_log.start_time
                    ongoing_time = (now - now.replace(
                        hour=start_time.hour, minute=start_time.minute, second=start_time.second
                    )).total_seconds() / 60
                    ongoing_time_log_id = time_log.id

            kwargs.update({
                "time_logged_str": get_humanised_time_str(total_time_logged),
                "ongoing_time_str": get_humanised_time_str(ongoing_time) if ongoing_time else None,
                "ongoing_time_log_id": ongoing_time_log_id
            })

            scrum_entries.append(kwargs)

        return {
            "record_date_str": "{}".format(day_entry.record_date),
            "day_time_logged_str": get_humanised_time_str(day_entry.time_logged or 0),
            "scrum_entries": scrum_entries,
            "statuses": ScrumEntry.FINAL_STATUS_CHOICES,
        }


    @classmethod
    def get_full_context_for_html_render(cls, day_entry_id):
        day_entry = cls.objects.prefetch_related(
            'tags',
            Prefetch(
                'journalentry_set',
                queryset=JournalEntry.active_qs().order_by('order').prefetch_related('tags'),
                to_attr='journal_entries'
            ),
            Prefetch(
                'scrumentry_set',
                queryset=ScrumEntry.active_qs().order_by('order').prefetch_related('tags').prefetch_related(
                    Prefetch('timelog_set', TimeLog.active_qs().filter(duration__isnull=False), to_attr='time_logs'),
                ),
                to_attr='scrum_entries'
            )
        ).get(id=day_entry_id)

        context = {
            "record_date_str": "{}".format(day_entry.record_date),
            "day_summary": day_entry.day_summary,
            "scrum_summary": day_entry.scrum_summary,
            "day_time_logged_str": get_humanised_time_str(day_entry.time_logged or 0),
            "day_tags_str": " ".join(["#{}".format(tag.name) for tag in day_entry.tags.all()])
        }

        scrum_entries = []
        for scrum_entry in day_entry.scrum_entries:
            scrum_entries.append({
                "title": scrum_entry.title,
                "notes": scrum_entry.notes,
                "final_status": scrum_entry.get_final_status_html(),
                "tags_str": " ".join(["#{}".format(tag.name) for tag in scrum_entry.tags.all()]),
                "time_logged_str": get_humanised_time_str(sum([log.duration for log in scrum_entry.time_logs]))
            })

        journal_entries = []
        for journal_entry in day_entry.journal_entries:
            journal_entries.append({
                "title": journal_entry.title,
                "response": journal_entry.response,
                "tags_str": " ".join(["#{}".format(tag.name) for tag in journal_entry.tags.all()])
            })

        context['scrum_entries'] = scrum_entries
        context['journal_entries'] = journal_entries

        return context


class DayEntryTagStat(models.Model):
    day_entry = models.ForeignKey(DayEntry, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    time_logged = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(60 * 24, message="You can't log more than 24 hours in a day")],
        help_text="Total time logged in the day, for the tag, in minutes"
    )

    class Meta:
        unique_together = (('day_entry', 'tag'),)

    @classmethod
    def create_tag_stats_for_day_entry(cls, day_entry_id, tagged_time):
        stats_to_update = cls.objects.filter(day_entry_id=day_entry_id, tag_id__in=tagged_time.keys())

        for stat in stats_to_update:
            stat.time_logged = tagged_time.pop(stat.tag_id)

        stats_to_create = [
            cls(day_entry_id=day_entry_id, tag_id=tag_id, time_logged=logged_time)
            for tag_id, logged_time in tagged_time.items()
        ]

        with transaction.atomic():
            bulk_update(stats_to_update, update_fields=['time_logged'])
            cls.objects.bulk_create(stats_to_create)


class JournalEntryTemplate(CommonInfoAbstractModel):
    title = models.CharField(max_length=128, help_text="What do you want to answer?")
    response = models.TextField(
        null=True, blank=True,
        help_text="Template for the response. Whatever is specified here will be copied to the day entry as is."
    )
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.title)


class JournalEntry(CommonInfoAbstractModel):
    day_entry = models.ForeignKey(DayEntry, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    response = models.TextField(null=True, blank=True)
    order = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name_plural = 'Journal Entries'

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.title)


class RepeatingScrumEntry(CommonInfoAbstractModel):
    title = models.CharField(max_length=128)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name_plural = 'Repeating Scrum Entries'

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.title)


class ScrumEntry(CommonInfoAbstractModel):
    FINAL_STATUS_COMPLETED = 1
    FINAL_STATUS_INCOMPLETE = 2
    FINAL_STATUS_DROPPED = 3

    FINAL_STATUS_CHOICES = (
        (FINAL_STATUS_COMPLETED, "Completed"),
        (FINAL_STATUS_INCOMPLETE, "Incomplete"),
        (FINAL_STATUS_DROPPED, "Dropped")
    )

    FINAL_STATUS_CHOICES_DICT = dict(FINAL_STATUS_CHOICES)
    FINAL_STATUS_CHOICES_DICT[None] = ""

    FINAL_STATUS_COLORS = {
        FINAL_STATUS_COMPLETED: 'green',
        FINAL_STATUS_INCOMPLETE: 'red',
        FINAL_STATUS_DROPPED: 'orange',
        None: ''
    }

    FINAL_STATUS_BOOTSTRAP_CLASSES = {
        FINAL_STATUS_COMPLETED: 'list-group-item-success',
        FINAL_STATUS_INCOMPLETE: 'list-group-item-danger',
        FINAL_STATUS_DROPPED: 'list-group-item-warning',
        None: ''
    }

    day_entry = models.ForeignKey(DayEntry, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, help_text="What task do you have to do?")
    notes = models.TextField(null=True, blank=True)
    final_status = models.PositiveSmallIntegerField(choices=FINAL_STATUS_CHOICES, null=True, blank=True)
    order = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name_plural = 'Scrum Entries'

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.title)

    def get_final_status_html(self):
        status = ScrumEntry.FINAL_STATUS_CHOICES_DICT[self.final_status]
        color = ScrumEntry.FINAL_STATUS_COLORS[self.final_status]

        return mark_safe("<span style='color:{0}'>{1}</span>".format(color, status))


class TimeLog(CommonInfoAbstractModel):
    scrum_entry = models.ForeignKey(ScrumEntry, on_delete=models.CASCADE)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    duration = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MaxValueValidator(60*24, message="You can't log more than 24 hours in a day")],
        help_text="Time in minutes"
    )

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            now = datetime.datetime.now()
            self.duration = (
                    now.replace(
                        hour=self.end_time.hour, minute=self.end_time.minute, second=self.end_time.second
                    )
                    -
                    now.replace(
                        hour=self.start_time.hour, minute=self.start_time.minute, second=self.start_time.second
                    )
            ).total_seconds() / 60

        super(TimeLog, self).save(*args, **kwargs)

    def clean(self):
        if not any([self.start_time, self.end_time, self.duration]):
            raise ValidationError("One of start_time, end_time or duration should be updated")
