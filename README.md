# dsm
Damn simple finite state machine

[![Build Status](https://travis-ci.org/marcinn/dsm.svg?branch=master)](https://travis-ci.org/marcinn/dsm)

## About

DSM is a observable simple finite state machine implementation for Python.
Transitions may be programmed declaratively or imperatively.
Inputs and state changes are emitting observable events.

## Requirements

  - Python 2.7, 3.5, 3.6
  - ``observable``
  - ``six`` for compatibility between Python 2 and Python 3

## Installation

pip install dsm


## Usage

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

## License

BSD
