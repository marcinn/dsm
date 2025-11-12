from django.conf import settings
from django.core.checks import Error
from django.core.management import call_command
from django.db import models
from django.test import TestCase

if not settings.configured:
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "dsm",
            "tests",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
    )
    import django

    django.setup()

from dsm.fields import StateMachineField

from tests.models import Order, OrderNoChoices


class StateMachineFieldTest(TestCase):
    def test_create_order(self):
        order = Order.objects.create()
        self.assertEqual(order.status, Order.Status.NEW)
        order.status.process("confirm")
        self.assertEqual(order.status, Order.Status.PROCESSING)
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PROCESSING)

    def test_deconstruct(self):
        # Order needs to be created for the field to be deconstructed
        Order.objects.create()
        field = Order._meta.get_field("status")
        name, path, args, kwargs = field.deconstruct()
        self.assertEqual(name, "status")
        self.assertEqual(path, "dsm.fields.StateMachineField")
        self.assertEqual(len(args), 1)
        self.assertEqual(kwargs["max_length"], 16)
        self.assertEqual(kwargs["default"], "new")

    def test_deconstruct_no_choices(self):
        # Order needs to be created for the field to be deconstructed
        OrderNoChoices.objects.create()
        field = OrderNoChoices._meta.get_field("status")
        name, path, args, kwargs = field.deconstruct()
        self.assertEqual(name, "status")
        self.assertEqual(path, "dsm.fields.StateMachineField")
        self.assertEqual(len(args), 1)
        self.assertEqual(kwargs["max_length"], 16)
        self.assertEqual(kwargs["default"], "new")

    def test_choices(self):
        # Order needs to be created for the field to have choices
        Order.objects.create()
        field = Order._meta.get_field("status")
        self.assertEqual(field.choices, Order.Status.choices)

    def test_choices_validator(self):
        field = StateMachineField(
            transitions=(("a", "op", "b"),),
            choices=(("a", "a"),),
            max_length=10,
        )
        field.name = "status"
        errors = field.check()
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], Error)
        self.assertEqual(errors[0].id, "dsm.E001")
        self.assertIn("b", errors[0].msg)


class StateMachineFieldChoiceTest(TestCase):
    def test_generating_choices(self):
        # Order needs to be created for the field to have choices
        OrderNoChoices.objects.create()
        field = OrderNoChoices._meta.get_field("status")
        self.assertEqual(
            sorted(list(zip(*field.choices))[0]),
            sorted(
                [
                    "new",
                    "processing",
                    "cancelled",
                    "sending",
                    "finished",
                ]
            ),
        )

    def test_generating_proper_choice_labels(self):
        # Order needs to be created for the field to have choices
        OrderNoChoices.objects.create()
        field = OrderNoChoices._meta.get_field("status")
        self.assertEqual(
            sorted(map(lambda x: x.label, list(zip(*field.choices))[1])),
            sorted(
                [
                    "New",
                    "Processing",
                    "Cancelled",
                    "Sending",
                    "Finished",
                ]
            ),
        )
