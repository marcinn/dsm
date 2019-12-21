import six
import collections
import observable


class FSMException(Exception):
    pass


class StateNotDefined(FSMException):
    pass


class UnknownTransition(FSMException):
    pass


class AlreadyRegistered(FSMException):
    pass


class Transitions(object):
    def __init__(self, transitions=None, fallbacks=None):
        self._allstates = set()
        self._states = collections.defaultdict(dict)
        self._fallbacks = {}

        if transitions:
            for from_state, value, to_state in transitions:
                if isinstance(value, (list, tuple)):
                    func = self.register_many
                else:
                    func = self.register
                func(from_state, value, to_state)

        if fallbacks:
            for from_state, to_state in fallbacks:
                self.register_fallback(from_state, to_state)

    def has_state(self, state):
        return state in self._allstates

    def register(self, from_state, value, to_state):
        if from_state in self._states and value in self._states[from_state]:
            raise AlreadyRegistered(
                'Transition for `%s` is already registered for state `%s`' % (
                    value, from_state))
        self._states[from_state][value] = to_state
        self._allstates.update([from_state, to_state])

    def register_many(self, from_state, values, to_state):
        for value in values:
            self.register(from_state, value, to_state)

    def register_fallback(self, from_state, to_state):
        """
        Registers fallback transition which will be used
        when there is no registered transition for input

        >>> import string
        >>> class DigitsDetectorMachine(StateMachine):
        ...     class Meta:
        ...         initial = 'letter'
        ...         transitions = (
        ...             ('letter', list(string.digits), 'digit'),  # 0-9 -> digit  # NOQA
        ...             ('digit', list(string.digits), 'digit'),  # 0-9 -> stay in digit  # NOQA
        ...         )
        ...         fallbacks = (
        ...             ('digit', 'letter'),  # non-digit -> letter
        ...             ('letter', 'letter'),  # non-digit -> stay in letter
        ...         )

        >>> output = []
        >>> dd = DigitsDetectorMachine()
        >>> dd.when('digit', output.append)
        >>> dd.process_many('test1234test4321')
        'digit'
        >>> ''.join(output)
        '12344321'
        """

        if from_state in self._fallbacks:
            raise AlreadyRegistered(
                'Fallback transition for `%s` '
                'is already registered' % from_state)

        self._fallbacks[from_state] = to_state
        self._allstates.update([from_state, to_state])

    def can(self, value, current_state):
        return bool(
                self._states.get(current_state) and
                self._states[current_state].get(value))

    def execute(self, value, current_state):
        try:
            return self._states[current_state][value]
        except KeyError:
            try:
                return self._fallbacks[current_state]
            except KeyError:
                raise UnknownTransition(
                    'Can not find transition for `%s` in state `%s`' % (
                                                    value, current_state))


class MetaMachine(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(MetaMachine, cls).__new__

        parents = [b for b in bases if isinstance(b, MetaMachine)]
        if not parents:
            new_class = super_new(cls, name, bases, attrs)
            cls.add_exception_classes(new_class)
            return new_class

        meta = attrs.pop('Meta', None)

        class Options(object):
            def __init__(self, meta):
                self.transitions = Transitions(
                        transitions=getattr(meta, 'transitions', None),
                        fallbacks=getattr(meta, 'fallbacks', None))
                self.initial = getattr(meta, 'initial', None)

        new_class = super_new(cls, name, bases, {})
        cls.add_exception_classes(new_class)
        setattr(new_class, '_meta', Options(meta))

        return new_class

    def add_exception_classes(new_class):
        setattr(new_class, 'FSMException', FSMException)
        setattr(new_class, 'UnknownTransition', UnknownTransition)


class StateMachine(six.with_metaclass(MetaMachine, object)):
    def __init__(self, initial=None, transitions=None):
        """
        >>> import string
        >>> class SumatorMachine(StateMachine):
        ...     class Meta:
        ...         initial = 'init'
        ...         transitions = (
        ...             ('init', list(string.digits), 'digit_enter'),
        ...             ('digit_enter', list(string.digits), 'digit_enter'),
        ...             ('digit_enter', '=', 'summarize'),
        ...         )

        >>> class Sumator(object):
        ...     def __init__(self):
        ...         self.fsm = SumatorMachine()
        ...         self.fsm.when('summarize', self._calculate)
        ...         self.fsm.when('digit_enter', self._store_digit)
        ...     def _store_digit(self, value):
        ...         self.digits.append(int(value))
        ...     def _calculate(self, value):
        ...         self.result = sum(self.digits)
        ...     def summarize(self, valuestring):
        ...         self.digits = []
        ...         self.result = None
        ...         self.fsm.reset()
        ...         self.fsm.process_many(valuestring+'=')
        ...         return self.result

        >>> sumator = Sumator()
        >>> sumator.summarize('666')
        18
        """

        meta = getattr(self, '_meta', None)
        self._eventhandler = observable.Observable()
        self._transitions = transitions or getattr(
                                meta, 'transitions', None) or []
        self._initial = initial or getattr(meta, 'initial', None)
        self._state = None
        self._inputhandlers = collections.defaultdict(list)
        self._eventhandler.on('input', self._inputhandler)
        self.reset()

    @property
    def state(self):
        return self._state

    def process(self, value):
        new_state = self._transitions.execute(value, self.state)

        if not self.state == new_state:
            self._eventhandler.trigger(
                    'change', state=new_state, previous=self.state)

        self._state = new_state
        self._eventhandler.trigger('input', state=new_state, value=value)

        return self.state

    def process_many(self, values):
        for value in values:
            self.process(value)
        return self.state

    def can(self, value):
        return self._transitions.can(value, self.state)

    def reset(self):
        if not self._transitions.has_state(self._initial):
            raise StateNotDefined(self._initial)

        old_state = self._state
        self._state = self._initial
        self._eventhandler.trigger(
                'change', state=self._state, previous=old_state)
        self._eventhandler.trigger('reset')
        return self.state

    def when(self, state, func):
        self._inputhandlers[state].append(func)

    def _inputhandler(self, state, value):
        for x in self._inputhandlers[state]:
            x(value)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
