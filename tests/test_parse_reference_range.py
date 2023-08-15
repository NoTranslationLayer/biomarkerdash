import unittest
from biomarkerdash.utils import parse_reference_range

class TestParseReferenceRange(unittest.TestCase):

    def test_nan(self):
        self.assertEqual(parse_reference_range('nan'), (None, None))
        self.assertEqual(parse_reference_range('NAN'), (None, None))
        self.assertEqual(parse_reference_range('NaN'), (None, None))

    def test_zero(self):
        self.assertEqual(parse_reference_range('0'), (0.0, 0.0))

    def test_less_than_format(self):
        self.assertEqual(parse_reference_range('<5.7'), (None, 5.7))
        self.assertEqual(parse_reference_range('<130'), (None, 130.0))

    def test_greater_than_format(self):
        self.assertEqual(parse_reference_range('>5.7'), (5.7, None))
        self.assertEqual(parse_reference_range('>130'), (130.0, None))

    def test_or_equal_format(self):
        self.assertEqual(parse_reference_range('> OR = 60'), (60.0, None))
        self.assertEqual(parse_reference_range('>=125'), (125.0, None))
        self.assertEqual(parse_reference_range('< OR = 80'), (None, 80.0))

    def test_or_less_format(self):
        self.assertEqual(parse_reference_range('0.2 OR LESS'), (None, 0.2))

    def test_standard_format(self):
        self.assertEqual(parse_reference_range('3.5-5.3'), (3.5, 5.3))
        self.assertEqual(parse_reference_range('135-146'), (135.0, 146.0))

    def test_special_format(self):
        self.assertEqual(parse_reference_range('-2.0 - +2.0'), (-2.0, 2.0))

    def test_fail_format(self):
        self.assertEqual(parse_reference_range('unparsable'), (None, None))
        self.assertEqual(parse_reference_range(''), (None, None))

if __name__ == '__main__':
    unittest.main()
