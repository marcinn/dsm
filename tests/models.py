from django.db import models
from dsm.fields import StateMachineField


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        PROCESSING = "processing", "Processing"
        SENDING = "sending", "Sending"
        FINISHED = "finished", "Finished"
        CANCELLED = "cancelled", "Cancelled"

    status = StateMachineField(
        transitions=(
            (Status.NEW, ["confirm"], Status.PROCESSING),
            (Status.PROCESSING, ["cancel"], Status.CANCELLED),
            (Status.PROCESSING, ["send"], Status.SENDING),
            (Status.SENDING, ["deliver"], Status.FINISHED),
        ),
        choices=Status.choices,
        max_length=16,
        db_index=True,
        default=Status.NEW,
    )

    class Meta:
        app_label = "tests"


class OrderNoChoices(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        PROCESSING = "processing", "Processing"
        SENDING = "sending", "Sending"
        FINISHED = "finished", "Finished"
        CANCELLED = "cancelled", "Cancelled"

    status = StateMachineField(
        transitions=(
            (Status.NEW, ["confirm"], Status.PROCESSING),
            (Status.PROCESSING, ["cancel"], Status.CANCELLED),
            (Status.PROCESSING, ["send"], Status.SENDING),
            (Status.SENDING, ["deliver"], Status.FINISHED),
        ),
        max_length=16,
        db_index=True,
        default=Status.NEW,
    )

    class Meta:
        app_label = "tests"
