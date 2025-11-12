import os
import unittest

from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.test import TestCase
from dsm.fields import StateMachineField

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'dsm',
            'tests',
        ],
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
    )
    import django
    django.setup()

from tests.models import Order


class StateMachineFieldTest(TestCase):
    def test_create_order(self):
        order = Order.objects.create()
        self.assertEqual(order.status, Order.Status.NEW)
        order.status.process('confirm')
        self.assertEqual(order.status, Order.Status.PROCESSING)
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PROCESSING)

    def test_deconstruct(self):
        # Order needs to be created for the field to be deconstructed
        Order.objects.create()
        field = Order._meta.get_field('status')
        name, path, args, kwargs = field.deconstruct()
        self.assertEqual(name, 'status')
        self.assertEqual(path, 'dsm.fields.StateMachineField')
        self.assertEqual(len(args), 1)
        self.assertEqual(kwargs['max_length'], 16)
        self.assertEqual(kwargs['default'], 'new')
        self.assertEqual(kwargs['choices'], Order.Status.choices)

    def test_choices(self):
        # Order needs to be created for the field to have choices
        Order.objects.create()
        field = Order._meta.get_field('status')
        self.assertEqual(field.choices, Order.Status.choices)

