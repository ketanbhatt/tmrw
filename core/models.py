import datetime

from django.core.validators import MaxValueValidator
from django.db import models

from common.models import CommonInfoAbstractModel


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


class DayEntryTagStat(models.Model):
    day_entry = models.ForeignKey(DayEntry, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    time_logged = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(60 * 24, message="You can't log more than 24 hours in a day")],
        help_text="Total time logged in the day, for the tag, in minutes"
    )


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
    template = models.ForeignKey(JournalEntryTemplate, on_delete=models.CASCADE)
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

    day_entry = models.ForeignKey(DayEntry, on_delete=models.CASCADE)
    repeated_scrum_entry = models.ForeignKey(RepeatingScrumEntry, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, help_text="What task do you have to do?")
    notes = models.TextField(null=True, blank=True)
    final_status = models.PositiveSmallIntegerField(choices=FINAL_STATUS_CHOICES, null=True, blank=True)
    order = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name_plural = 'Scrum Entries'

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.title)


class StartEndTimeLog(CommonInfoAbstractModel):
    scrum_entry = models.ForeignKey(ScrumEntry, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()


class ManualTimeLog(CommonInfoAbstractModel):
    scrum_entry = models.ForeignKey(ScrumEntry, on_delete=models.CASCADE)
    duration = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(60*24, message="You can't log more than 24 hours in a day")],
        help_text="Time in minutes"
    )