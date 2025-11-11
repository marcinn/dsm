import unittest

from dsm import StateMachine, Transitions, UnknownTransition, AlreadyRegistered, StateNotDefined


class TestTransitions(unittest.TestCase):
    def test_register(self):
        t = Transitions()
        t.register('a', '1', 'b')
        self.assertTrue(t.has_state('a'))
        self.assertTrue(t.has_state('b'))
        self.assertFalse(t.has_state('c'))
        self.assertTrue(t.can('1', 'a'))
        self.assertFalse(t.can('2', 'a'))
        self.assertEqual('b', t.execute('1', 'a'))

    def test_register_already_registered(self):
        t = Transitions()
        t.register('a', '1', 'b')
        with self.assertRaises(AlreadyRegistered):
            t.register('a', '1', 'c')

    def test_register_many(self):
        t = Transitions()
        t.register_many('a', ['1', '2'], 'b')
        self.assertTrue(t.can('1', 'a'))
        self.assertTrue(t.can('2', 'a'))
        self.assertEqual('b', t.execute('1', 'a'))
        self.assertEqual('b', t.execute('2', 'a'))

    def test_register_fallback(self):
        t = Transitions()
        t.register_fallback('a', 'b')
        self.assertEqual('b', t.execute('anything', 'a'))

    def test_register_fallback_already_registered(self):
        t = Transitions()
        t.register_fallback('a', 'b')
        with self.assertRaises(AlreadyRegistered):
            t.register_fallback('a', 'c')

    def test_execute_unknown_transition(self):
        t = Transitions()
        t.register('a', '1', 'b')
        with self.assertRaises(UnknownTransition):
            t.execute('2', 'a')

    def test_init_with_transitions(self):
        transitions = [('a', '1', 'b')]
        t = Transitions(transitions=transitions)
        self.assertTrue(t.can('1', 'a'))
        self.assertEqual('b', t.execute('1', 'a'))

    def test_init_with_fallbacks(self):
        fallbacks = [('a', 'b')]
        t = Transitions(fallbacks=fallbacks)
        self.assertEqual('b', t.execute('anything', 'a'))


class DigitsDetectorMachine(StateMachine):
    class Meta:
        initial = 'letter'
        transitions = (
            ('letter', [str(i) for i in range(10)], 'digit'),
            ('digit', [str(i) for i in range(10)], 'digit'),
        )
        fallbacks = (
            ('digit', 'letter'),
            ('letter', 'letter'),
        )


class TestDigitsDetector(unittest.TestCase):
    def test_simple(self):
        output = []
        dd = DigitsDetectorMachine()
        dd.when('digit', output.append)
        self.assertEqual('digit', dd.process_many('test1234test4321'))
        self.assertEqual('12344321', ''.join(output))


class SumatorMachine(StateMachine):
    class Meta:
        initial = 'init'
        transitions = (
            ('init', [str(i) for i in range(10)], 'digit_enter'),
            ('digit_enter', [str(i) for i in range(10)], 'digit_enter'),
            ('digit_enter', '=', 'summarize'),
        )


class Sumator(object):
    def __init__(self):
        self.fsm = SumatorMachine()
        self.fsm.when('summarize', self._calculate)
        self.fsm.when('digit_enter', self._store_digit)

    def _store_digit(self, value):
        self.digits.append(int(value))

    def _calculate(self, value):
        self.result = sum(self.digits)

    def summarize(self, valuestring):
        self.digits = []
        self.result = None
        self.fsm.reset()
        self.fsm.process_many(valuestring + '=')
        return self.result


class TestSumator(unittest.TestCase):
    def test_sumator(self):
        sumator = Sumator()
        self.assertEqual(18, sumator.summarize('666'))


class TestStateMachine(unittest.TestCase):
    def test_init(self):
        transitions = Transitions(transitions=[('a', '1', 'b')])
        sm = StateMachine(initial='a', transitions=transitions)
        self.assertEqual('a', sm.state)
        self.assertTrue(sm.can('1'))
        self.assertFalse(sm.can('2'))

    def test_state_not_defined(self):
        with self.assertRaises(StateNotDefined):
            StateMachine(initial='unknown')

    def test_process(self):
        transitions = Transitions(transitions=[('a', '1', 'b')])
        sm = StateMachine(initial='a', transitions=transitions)
        self.assertEqual('b', sm.process('1'))
        self.assertEqual('b', sm.state)

    def test_events(self):
        transitions = Transitions(transitions=[('a', '1', 'b')])
        sm = StateMachine(initial='a', transitions=transitions)

        change_event_args = {}
        def on_change(**kwargs):
            change_event_args.update(kwargs)
        sm._eventhandler.on('change', on_change)

        input_event_args = {}
        def on_input(**kwargs):
            input_event_args.update(kwargs)
        sm._eventhandler.on('input', on_input)

        sm.process('1')

        self.assertEqual({'state': 'b', 'previous': 'a'}, change_event_args)
        self.assertEqual({'state': 'b', 'value': '1'}, input_event_args)