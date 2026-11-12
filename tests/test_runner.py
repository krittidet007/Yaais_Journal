"""Player scripts run safely on every platform — including Windows,
where there is no SIGALRM and a ``while True:`` must still stop."""

import sys
import time
import unittest

from game import runner as R


class TestRunner(unittest.TestCase):

    def _without_signal(self):
        """Run the Windows code path (trace guard instead of SIGALRM)."""
        self.addCleanup(setattr, R, 'HAVE_SIGNAL', R.HAVE_SIGNAL)
        self.addCleanup(sys.settrace, None)
        R.HAVE_SIGNAL = False

    def test_plain_code_runs(self):
        result = R.run_code('total = sum(range(10))\nprint(total)')
        self.assertTrue(result['ok'])
        self.assertEqual(result['output'], '45\n')
        self.assertEqual(result['env']['total'], 45)

    def test_error_names_the_line(self):
        result = R.run_code('a = 1\nb = 0\nprint(a / b)')
        self.assertFalse(result['ok'])
        self.assertEqual(result['line'], 3)
        self.assertIn('ZeroDivisionError', result['message'])

    def test_blank_script_is_refused(self):
        self.assertFalse(R.run_code('   \n  ')['ok'])

    def test_infinite_loop_stops_without_sigalrm(self):
        """The Windows path: no signal, so the deadline trace fires."""
        self._without_signal()
        started = time.monotonic()
        result = R.run_code('x = 0\nwhile True:\n    x += 1', timeout=0.5)
        self.assertFalse(result['ok'])
        self.assertIn('too long', result['message'])
        self.assertLess(time.monotonic() - started, 6.0)
        self.assertIsNone(sys.gettrace())      # the guard never lingers

    def test_normal_code_is_untraced_afterwards(self):
        self._without_signal()
        result = R.run_code("print('still here')", timeout=1.0)
        self.assertTrue(result['ok'])
        self.assertEqual(result['output'], 'still here\n')
        self.assertIsNone(sys.gettrace())


if __name__ == '__main__':
    unittest.main()
