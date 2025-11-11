import unittest

from dsm import StateMachine


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
