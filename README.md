# dsm
Damn simple finite state machine

![PyPI - Version](https://img.shields.io/pypi/v/dsm)
![PyPI - Status](https://img.shields.io/pypi/status/dsm)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dsm)
![PyPI - Downloads](https://img.shields.io/pypi/dm/dsm)
![PyPI - Format](https://img.shields.io/pypi/format/dsm)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/marcinn/dsm/.github%2Fworkflows%2Fci.yml)
![PyPI - License](https://img.shields.io/pypi/l/dsm)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/dsm)


## About

DSM is a observable simple finite state machine implementation for Python.
Transitions may be programmed declaratively or imperatively.
Inputs and state changes are emitting observable events.

## Requirements

  - Python 3.8+
  - ``observable``

## Installation

pip install dsm


## Usage

### Django integration

It is possible to integrate `dsm` with Django models by
declaring a `StateMachineField`.

```python

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
```

Now you can create an `Order` and check it's status:

```python
>>> order = Order.objects.create()
>>> order.status
new
>>> type(order.status)
dsm.fields.MachineState
```

The string representation of `status` field is same as state name
provided in transitions declaration, but internally there is always
`dsm.fields.MachineState` instance.


### Declarative


FSM declaration:

```python
import string
import dsm

class SumatorMachine(dsm.StateMachine):
    class Meta:
        initial = 'init'
        transitions = (
            ('init', list(string.digits), 'digit_enter'),
            ('digit_enter', list(string.digits), 'digit_enter'),
            ('digit_enter', '=', 'summarize'),
        )
```

### Usage:

Initialization:

```python
fsm = SumatorMachine()
```

Processing one value:

```python
fsm.process(value)
```

Processing multiple values:

```python
fsm.process_many(iterable)
```

Gathering the current state:

```python
>>> fsm.state
'summarize'
```

Resetting to the intial state:

```python
fsm.reset()
```

Listening on events:

```python
fsm.when('state', func)
```

Events example:

```python
>>> the_sum = 0

>>> def add_digit(x): global the_sum; the_sum += int(x)
>>> def reset(x): global the_sum; the_sum = 0

>>> fsm = SumatorMachine()
>>> fsm.when('digit_enter', add_digit)
>>> fsm.when('init', reset)

>>> fsm.process_many('666=')
'summarize'

>>> the_sum
18
```

Events example (class based):

```python
>>> class Sumator(object):
...     def __init__(self):
...         self.total = 0
...         self.fsm = SumatorMachine()
...         self.fsm.when('digit_enter', self.add)
...         self.fsm.when('init', self.reset)
...
...     def add(self, x):
...         self.total += int(x)
...
...     def reset(self, x):
...         self.total = 0
...
...     def summarize(self, values):
...         self.fsm.reset()
...         self.fsm.process_many(values+'=')
...         return self.total

>>> s = Sumator()
>>> s.summarize('666')
18
```
### Imperative

```python
import string
import dsm

fsm = dsm.StateMachine(
        initial='init',
        transitions=dsm.Transitions((
                ('init', list(string.digits), 'digit_enter'),
                ('digit_enter', list(string.digits), 'digit_enter'),
                ('digit_enter', '=', 'summarize'),
            ))
        )
```

## License

BSD
