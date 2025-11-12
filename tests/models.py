from django.db import models
from django.utils.translation import gettext_lazy as _
from dsm.fields import StateMachineField

class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', _('New')
        PROCESSING = 'processing', _('Processing')
        SENDING = 'sending', _('Sending')
        FINISHED = 'finished', _('Finished')
        CANCELLED = 'cancelled', _('Cancelled')

    status = StateMachineField(
        transitions=(
            (Status.NEW, ['confirm'], Status.PROCESSING),
            (Status.PROCESSING, ['cancel'], Status.CANCELLED),
            (Status.PROCESSING, ['send'], Status.SENDING),
            (Status.SENDING, ['deliver'], Status.FINISHED),
        ),
        choices=Status.choices,
        max_length=16,
        db_index=True,
        default=Status.NEW,
    )

    class Meta:
        app_label = 'tests'
