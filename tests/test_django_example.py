import os
import unittest

from django.conf import settings
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

# Configure Django settings for the test
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
        # Add this to avoid AppRegistryNotReady error in some cases
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
    )
    import django
    django.setup()


from dsm.fields import StateMachineField, MachineState
from tests.models import Order


class DjangoExampleTest(TestCase):
    def test_django_example(self):
        # Create an Order and check its status
        order = Order.objects.create()
        self.assertEqual(order.status, 'new')
        self.assertIsInstance(order.status, MachineState)

        # Test transitions
        order.status.process('confirm')
        self.assertEqual(order.status, 'processing')

        order.status.process('send')
        self.assertEqual(order.status, 'sending')

        order.status.process('deliver')
        self.assertEqual(order.status, 'finished')

        # Test another transition path
        order_to_cancel = Order.objects.create()
        self.assertEqual(order_to_cancel.status, 'new')
        order_to_cancel.status.process('confirm')
        self.assertEqual(order_to_cancel.status, 'processing')
        order_to_cancel.status.process('cancel')
        self.assertEqual(order_to_cancel.status, 'cancelled')
