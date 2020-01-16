from django.db import models
from . import StateMachine, Transitions


__all__ = ['StateMachineField']


class MachineState:
    def __init__(self, instance, field, fsm):
        self.instance = instance
        self.field = field
        self.fsm = fsm

    def process(self, value):
        self.fsm.process(value)
        self.instance.__dict__[self.field.name] = self

    def process_many(self, values):
        self.fsm.process_many(values)
        self.instance.__dict__[self.field.name] = self

    def reset(self):
        self.fsm.reset()
        self.instance.__dict__[self.field.name] = self

    def __eq__(self, other):
        try:
            return self.fsm.state == other.fsm.state
        except AttributeError:
            return self.fsm.state == other

    def __repr__(self):
        return repr(self.fsm.state)

    def __str__(self):
        return str(self.fsm.state)

    def __hash__(self):
        return hash(self.fsm.state)


class StateDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        value = instance.__dict__[self.field.name]
        if value is None:
            return value
        if isinstance(value, MachineState):
            return value
        return MachineState(
            instance, self.field, self.field._create_fsm(value))

    def __set__(self, instance, value):
        if value is not None:
            value = MachineState(
                instance, self.field, self.field._create_fsm(value))
        instance.__dict__[self.field.name] = value
        """
        current_value = instance.__dict__.get(self.field.name)
        if value is not None:
            if current_value:
                fsm = self.field._create_fsm(current_value)
                fsm.process(value)
            else:
                fsm = self.field._create_fsm(value)
            value = fsm.state
        instance.__dict__[self.field.name] = value
        """


class StateMachineFieldMixin:
    descriptor_class = StateDescriptor

    def __init__(self, transitions, *args, **kwargs):
        self.transitions = transitions
        super().__init__(*args, **kwargs)

    def _create_fsm(self, initial):
        return StateMachine(
            initial=initial, transitions=Transitions(self.transitions))

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)


class StateMachineField(StateMachineFieldMixin, models.CharField):
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        path = 'dsm.fields.StateMachineField'
        args.insert(0, self.transitions)
        return name, path, args, kwargs
