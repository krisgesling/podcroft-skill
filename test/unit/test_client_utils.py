import unittest

from podcast_client.episode import get_ms_from_hms


class DurationConversion(unittest.TestCase):
    def test_hms_to_ms(self):
        self.assertEqual(get_ms_from_hms("00:00:01"), 1000)
        self.assertEqual(get_ms_from_hms("00:01:01"), 61000)
        self.assertEqual(get_ms_from_hms("14:37:05"), 50400000 + 2220000 + 5000)
